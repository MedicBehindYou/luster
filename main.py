# main.py
#    luster
#    Copyright (C) 2024  MedicBehindYou
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import config_loader
import config_updater
import sys
if not os.path.exists("/config/config.ini"):
    config_loader.create_config()
config = config_loader.load_config()

if not config_loader.check_config_entry(config, 'Version', 'version'):
    config_loader.add_version()

config = config_loader.load_config()

if config:
    CONFIG_VERSION = (config['Version']['version'])

if not CONFIG_VERSION == '2.0.0':
    cfgupdateYN = input('Config is currently out of date. Run update (y/n): ')
    if cfgupdateYN == 'y' or cfgupdateYN == 'Y':
        config_updater.update_config(CONFIG_VERSION)
        config = config_loader.load_config()
        print('Please review/update any added values in your config.')
        sys.exit()
    elif cfgupdateYN == 'n' or cfgupdateYN == 'N':
        print('Update canceled, closing.')
        sys.exit()
    else:
        print('Invalid option.')
        sys.exit()  

import sqlite3
import subprocess
import threading
import time
import sys
from datetime import datetime
from logger import log
from importer import bulk_import_tags, single_import
from db_setup import setup_database
from db_backup import create_backup, manage_backups
from organize import reorder_table
from uncensor import uncensor
from db_migration import has_version_table, current_version, migrate
from no_ai import no_ai
from collectors import rule34, gelbooru, danbooru
from manifest import collect
from preskip import preskip
from luscious import api, utils, downloader
import booruDown
import utilities
import nhentai


row_lock = threading.Lock()

if config:
    DATABASE_DB = (config['General']['database_db'])
    LOG_TXT = (config['General']['log_txt'])  
    LUSCIOUS_COOKIE_NAME = (config['Luscious']['cookie_name'])
    LUSCIOUS_COOKIE_VALUE = (config['Luscious']['cookie_value'])       
else:
    log('Configuration not loaded.')
    sys.exit()

if not os.path.exists(DATABASE_DB):
    setup_database()


if not has_version_table(DATABASE_DB):
    migrate()
if current_version() != "2.4.0":
    migrateYN = input('DB is currently out of date. Run migration (y/n): ')
    if migrateYN == 'y' or migrateYN == 'Y':
        migrate()
    elif migrateYN == 'n' or migrateYN == 'N':
        print('Migration canceled, closing.')
        sys.exit()
    else:
        print('Invalid option.')
        sys.exit()  

if len(sys.argv) > 1 and sys.argv[1] == "--setup":
    setup_database()
    sys.exit()

if len(sys.argv) > 1 and sys.argv[1] == "--bulk":
    if len(sys.argv) > 2:
        create_backup()
        bulk_import_tags(sys.argv[2]) 
        manage_backups()
    else:
        bulk_import_tags('/config/entries.txt') 
    sys.exit()    

if len(sys.argv) > 1 and sys.argv[1] == "--single" or len(sys.argv) > 1 and sys.argv[1] == "-s":
    try:   
        create_backup()
        if len(sys.argv) == 3:
            arg1 = sys.argv[2]
            single_import(arg1)
        elif len(sys.argv) == 4:
            arg1 = sys.argv[2]
            arg2 = sys.argv[3]
            single_import(arg1, arg2)
        elif len(sys.argv) == 5:
            arg1 = sys.argv[2]
            arg2 = sys.argv[3]            
            arg3 = sys.argv[4]
            single_import(arg1, arg2, arg3)
        else:
            print("Usage --single <tag> <optional - siteNum> <optional(siteNum req.) genre> or -s <tag> < optional - siteNum> <optional(siteNum req.) genre>")
        manage_backups()
    except:
        print("Usage --single <tag> <optional - siteNum> <optional(siteNum req.) genre> or -s <tag> < optional - siteNum> <optional(siteNum req.) genre>")
    sys.exit()



if len(sys.argv) > 1 and sys.argv[1] == "--organize":
    create_backup()
    reorder_table(DATABASE_DB)
    manage_backups()
    sys.exit()

if len(sys.argv) > 1 and sys.argv[1] == "--uncensor":
    create_backup()
    uncensor(DATABASE_DB)
    manage_backups()
    sys.exit()

if len(sys.argv) > 1 and sys.argv[1] == "--no_ai":
    create_backup()
    no_ai(DATABASE_DB)
    manage_backups()
    sys.exit()

if len(sys.argv) > 1 and sys.argv[1] == "--collect":
    if len(sys.argv) > 2:
        create_backup()
        site = sys.argv[2]
        collect(site, DATABASE_DB)
        manage_backups()
    else:
        print("Usage: --collect <site>")
    sys.exit()

reverse_mode = False
if "-rev" in sys.argv or "--reverse" in sys.argv:
    reverse_mode = True

try:
    create_backup()

    conn = sqlite3.connect(DATABASE_DB, timeout=20)

    cursor = conn.cursor()

    log_file = open(LOG_TXT, 'a')

    while True:
        returnCode = None
        with row_lock:
            if reverse_mode:
                utilities.acquire_lock(conn)
                cursor.execute('SELECT name, id FROM tags WHERE complete = 0 AND running <> 1 ORDER BY ROWID DESC LIMIT 1')
                conn.commit()
            else:
                utilities.acquire_lock(conn)
                cursor.execute('SELECT name, id FROM tags WHERE complete = 0 AND running <> 1 LIMIT 1')
                conn.commit()
            
            row = cursor.fetchone()

        if row:
            tag = row[0]
            row_id = row[1]
            log(f'Starting processing tag: {tag}')
            utilities.acquire_lock(conn)
            cursor.execute("UPDATE tags SET running = '1' WHERE id = ?", (row_id,))
            conn.commit()

            utilities.acquire_lock(conn)
            cursor.execute("SELECT site FROM tags WHERE id = ?", (row_id,))
            siteQuery = cursor.fetchone()
            siteQuery = siteQuery[0]

            cursor.execute("SELECT genre FROM tags WHERE id = ?", (row_id,))
            genreQuery = cursor.fetchone()
            genre_ids = genreQuery[0]
            conn.commit()
            
        else:
            utilities.acquire_lock(conn)
            update_query = "UPDATE tags SET complete = 0 WHERE running != 1;"
            cursor.execute(update_query)
            conn.commit()
            log('All tags processed. Resetting for a new run.')
            break
        downTag = tag.split(',')      
        downTag = sorted(downTag)
        downloadList = []

        if siteQuery == 0:
            sites = ["rule34", "gelbooru", "danbooru"]            
            for site in sites:
                if site == 'rule34':
                    result = rule34.collector(downTag)
                    downloadList.extend(result)
                if site == 'gelbooru':
                    result = gelbooru.collector(downTag)
                    downloadList.extend(result)
                if site == 'danbooru' and not len(downTag) > 2:
                    result = danbooru.collector(downTag)
                    downloadList.extend(result)                    
            downloadList = preskip(downloadList, downTag)
            returnCode = booruDown.downloader(downloadList, downTag)
        elif siteQuery == 1: # Luscious artists
            artist = tag.lower()
            ids = api.luscious_artist_album_ids(artist)
            folderType = 'artists'
            for album_id in ids:
                title = api.luscious_album_name(album_id)
                picture_url_list = api.luscious_album_pictures(album_id)
                album_folder = utils.format_foldername(title)
                returnCode = downloader.download(title, picture_url_list, album_folder, tag, folderType)
        elif siteQuery == 2: # Luscious tags
            tag = tag.lower()
            folderType = 'tags'
            if genre_ids != '0':
                ids = api.luscious_tag_search(tag, genre_ids)
                if ids == []:
                    print(f'No items returned for tag: {tag}')
                    returnCode = 0
                else:
                    for album_id in ids:
                        title = api.luscious_album_name(album_id)
                        picture_url_list = api.luscious_album_pictures(album_id)
                        album_folder = utils.format_foldername(title)
                        returnCode = downloader.download(title, picture_url_list, album_folder, tag, folderType) 
            else:
                ids = api.luscious_tag_search(tag)
                for album_id in ids:
                    title = api.luscious_album_name(album_id)
                    picture_url_list = api.luscious_album_pictures(album_id)
                    album_folder = utils.format_foldername(title)
                    returnCode = downloader.download(title, picture_url_list, album_folder, tag, folderType)        
        elif siteQuery == 3:
            tag = tag.lower()
            nhentai_IDs = nhentai.api.fetch_albums(tag)
            nhentai_IDs = nhentai.preskip.album_skip(nhentai_IDs, tag)
            if nhentai_IDs == []:
                returnCode = 0
            else: 
                for album in nhentai_IDs:
                    returnCode = nhentai.downloader.album_downloader(album[1], album[2], album[0], tag)
        else:
            log(f"Unknown site: {site}")


        if returnCode == 0:
            try:
                utilities.acquire_lock(conn)
                current_timestamp = datetime.now()
                cursor.execute("UPDATE tags SET complete = 1, date = ? WHERE id = ?", (current_timestamp, row_id))
                cursor.execute("UPDATE tags SET running = '0' WHERE id = ?", (row_id,))
                conn.commit()
                log(f'Tag "{tag}" processed successfully.')
            except Exception as e:
                cursor.execute("ROLLBACK")
                error_message = f'Error processing tag "{tag}": {e}'
                log(error_message)
            else:
                conn.commit()
        elif returnCode == 1:
            with row_lock:
                utilities.acquire_lock(conn)
                cursor.execute("UPDATE tags SET running = '0' WHERE id = ?", (row_id,))
                conn.commit()
        elif returnCode is not None:
            log(f'Subprocess for tag "{tag}" was terminated with return code: {returnCode}')    
        else:
            utilities.acquire_lock(conn)
            cursor.execute("UPDATE tags SET running = '0' WHERE id = ?", (row_id,))
            conn.commit()

finally:
    if row is not None:
        utilities.acquire_lock(conn)
        cursor.execute("UPDATE tags SET running = '0' WHERE id = ?", (row_id,))
        conn.commit()
    manage_backups()

    conn.close()
    log_file.close()

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
import config_utils
import sys
if not os.path.exists("/config/config.ini"):
    config_utils.config_loader.create_config()
config = config_utils.config_loader.load_config()

if not config_utils.config_loader.check_config_entry(config, 'Version', 'version'):
    config_utils.config_loader.add_version()

config = config_utils.config_loader.load_config()

if config:
    CONFIG_VERSION = (config['Version']['version'])

if not CONFIG_VERSION == '3.0.0':
    cfgupdateYN = input('Config is currently out of date. Run update (y/n): ')
    if cfgupdateYN == 'y' or cfgupdateYN == 'Y':
        config_utils.config_updater.update_config(CONFIG_VERSION)
        config = config_utils.config_loader.load_config()
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
import nhentai
import db_utils
import booruCollectors
import luscious
import misc


row_lock = threading.Lock()

if config:
    DATABASE_DB = (config['General']['database_db'])
    LOG_TXT = (config['General']['log_txt'])  
    LUSCIOUS_COOKIE_NAME = (config['Luscious']['cookie_name'])
    LUSCIOUS_COOKIE_VALUE = (config['Luscious']['cookie_value'])       
else:
    misc.logger.log('Configuration not loaded.')
    sys.exit()

if not os.path.exists(DATABASE_DB):
    db_utils.db_setup.setup_database()


if not db_utils.db_migration.has_version_table(DATABASE_DB):
    db_utils.db_migration.migrate()
if db_utils.db_migration.current_version() != "2.7.0":
    migrateYN = input('DB is currently out of date. Run migration (y/n): ')
    if migrateYN == 'y' or migrateYN == 'Y':
        db_utils.db_migration.migrate()
    elif migrateYN == 'n' or migrateYN == 'N':
        print('Migration canceled, closing.')
        sys.exit()
    else:
        print('Invalid option.')
        sys.exit()  

if len(sys.argv) > 1 and sys.argv[1] == "--bulk":
    if len(sys.argv) > 2:
        db_utils.db_backup.create_backup()
        misc.importer.bulk(sys.argv[2]) 
        db_utils.db_backup.manage_backups()
    else:
        misc.importer.bulk('/config/entries.txt') 
    sys.exit()    

if len(sys.argv) > 1 and sys.argv[1] == "--single" or len(sys.argv) > 1 and sys.argv[1] == "-s":
    try:   
        db_utils.db_backup.create_backup()
        if len(sys.argv) == 3:
            arg1 = sys.argv[2]
            misc.importer.single(arg1)
        elif len(sys.argv) == 4:
            arg1 = sys.argv[2]
            arg2 = sys.argv[3]
            misc.importer.single(arg1, arg2)
        elif len(sys.argv) == 5:
            arg1 = sys.argv[2]
            arg2 = sys.argv[3]            
            arg3 = sys.argv[4]
            misc.importer.single(arg1, arg2, arg3)
        else:
            print("Usage --single <tag> <optional - siteNum> <optional(siteNum req.) genre> or -s <tag> < optional - siteNum> <optional(siteNum req.) genre>")
        db_utils.db_backup.manage_backups()
    except:
        print("Usage --single <tag> <optional - siteNum> <optional(siteNum req.) genre> or -s <tag> < optional - siteNum> <optional(siteNum req.) genre>")
    sys.exit()



if len(sys.argv) > 1 and sys.argv[1] == "--organize":
    db_utils.db_backup.create_backup()
    misc.organize.reorder_table(DATABASE_DB)
    db_utils.db_backup.manage_backups()
    sys.exit()

if len(sys.argv) > 1 and sys.argv[1] == "--uncensor":
    db_utils.db_backup.create_backup()
    misc.uncensor.add(DATABASE_DB)
    db_utils.db_backup.manage_backups()
    sys.exit()

if len(sys.argv) > 1 and sys.argv[1] == "--no_ai":
    db_utils.db_backup.create_backup()
    misc.no_ai.add(DATABASE_DB)
    db_utils.db_backup.manage_backups()
    sys.exit()

if len(sys.argv) > 1 and sys.argv[1] == "--collect":
    if len(sys.argv) > 2:
        db_utils.db_backup.create_backup()
        site = sys.argv[2]
        utils.manifest.collect(site, DATABASE_DB)
        db_utils.db_backup.manage_backups()
    else:
        print("Usage: --collect <site>")
    sys.exit()

reverse_mode = False
if "-rev" in sys.argv or "--reverse" in sys.argv:
    reverse_mode = True

try:
    db_utils.db_backup.create_backup()

    conn = sqlite3.connect(DATABASE_DB, timeout=20)

    cursor = conn.cursor()

    log_file = open(LOG_TXT, 'a')

    while True:
        returnCode = None
        with row_lock:
            if reverse_mode:
                misc.utilities.acquire_lock(conn)
                cursor.execute('SELECT name, id FROM tags WHERE complete = 0 AND running <> 1 ORDER BY ROWID DESC LIMIT 1')
                conn.commit()
            else:
                misc.utilities.acquire_lock(conn)
                cursor.execute('SELECT name, id FROM tags WHERE complete = 0 AND running <> 1 LIMIT 1')
                conn.commit()
            
            row = cursor.fetchone()

        if row:
            tag = row[0]
            row_id = row[1]
            misc.logger.log(f'Starting processing tag: {tag}')
            misc.utilities.acquire_lock(conn)
            cursor.execute("UPDATE tags SET running = '1' WHERE id = ?", (row_id,))
            conn.commit()

            misc.utilities.acquire_lock(conn)
            cursor.execute("SELECT site FROM tags WHERE id = ?", (row_id,))
            siteQuery = cursor.fetchone()
            siteQuery = siteQuery[0]

            cursor.execute("SELECT genre FROM tags WHERE id = ?", (row_id,))
            genreQuery = cursor.fetchone()
            genre_ids = genreQuery[0]
            conn.commit()
            
        else:
            misc.utilities.acquire_lock(conn)
            update_query = "UPDATE tags SET complete = 0 WHERE running != 1;"
            cursor.execute(update_query)
            conn.commit()
            misc.logger.log('All tags processed. Resetting for a new run.')
            break
        downTag = tag.split(',')      
        downTag = sorted(downTag)
        downloadList = []

        if siteQuery == 0:
            sites = ["rule34", "gelbooru", "danbooru", "xbooru", "konachan", "yandere"]            
            for site in sites:
                if site == 'rule34':
                    result = booruCollectors.rule34.collector(downTag)
                    downloadList.extend(result)
                if site == 'gelbooru':
                    result = booruCollectors.gelbooru.collector(downTag)
                    downloadList.extend(result)
                if site == 'danbooru' and not len(downTag) > 2:
                    result = booruCollectors.danbooru.collector(downTag)
                    downloadList.extend(result)    
                if site == 'xbooru':
                    result = booruCollectors.xbooru.collector(downTag)
                    downloadList.extend(result)         
                if site == 'konachan':
                    result = booruCollectors.konachan.collector(downTag)
                    downloadList.extend(result)             
                if site == 'yandere':
                    result = booruCollectors.yandere.collector(downTag)
                    downloadList.extend(result)                                         
            downloadList = booruCollectors.preskip.booruSkip(downloadList, downTag)
            booruCollectors.booruDown.downloader(downloadList, downTag)
            returnCode = 0
        elif siteQuery == 1: # Luscious artists
            artist = tag.lower()
            ids = luscious.api.luscious_artist_album_ids(artist)
            folderType = 'artists'
            for album_id in ids:
                title = luscious.api.luscious_album_name(album_id)
                picture_url_list = luscious.api.luscious_album_pictures(album_id)
                album_folder = luscious.utils.format_foldername(title)
                luscious.downloader.download(title, picture_url_list, album_folder, tag, folderType)
            returnCode = 0
        elif siteQuery == 2: # Luscious tags
            tag = tag.lower()
            folderType = 'tags'
            if genre_ids != '0':
                ids = luscious.api.luscious_tag_search(tag, genre_ids)
                if ids == []:
                    print(f'No items returned for tag: {tag}')
                    returnCode = 0
                else:
                    for album_id in ids:
                        title = luscious.api.luscious_album_name(album_id)
                        picture_url_list = luscious.api.luscious_album_pictures(album_id)
                        album_folder = luscious.utils.format_foldername(title)
                        luscious.downloader.download(title, picture_url_list, album_folder, tag, folderType) 
                    returnCode = 0
            else:
                ids = luscious.api.luscious_tag_search(tag)
                for album_id in ids:
                    title = luscious.api.luscious_album_name(album_id)
                    picture_url_list = luscious.api.luscious_album_pictures(album_id)
                    album_folder = luscious.utils.format_foldername(title)
                    luscious.downloader.download(title, picture_url_list, album_folder, tag, folderType)     
                returnCode = 0   
        elif siteQuery == 3:
            tag = tag.lower()
            nhentai_IDs = nhentai.api.fetch_albums(tag)
            nhentai_IDs = nhentai.preskip.album_skip(nhentai_IDs, tag)
            if nhentai_IDs == []:
                returnCode = 0
            else: 
                for album in nhentai_IDs:
                    returnCode = nhentai.downloader.album_downloader(album[1], album[2], album[0], tag)
                returnCode = 0
        else:
            misc.logger.log(f"Unknown site: {site}")


        if returnCode == 0:
            try:
                misc.utilities.acquire_lock(conn)
                current_timestamp = datetime.now()
                cursor.execute("UPDATE tags SET complete = 1, date = ? WHERE id = ?", (current_timestamp, row_id))
                cursor.execute("UPDATE tags SET running = '0' WHERE id = ?", (row_id,))
                conn.commit()
                misc.logger.log(f'Tag "{tag}" processed successfully.')
            except Exception as e:
                cursor.execute("ROLLBACK")
                error_message = f'Error processing tag "{tag}": {e}'
                misc.logger.log(error_message)
            else:
                conn.commit()
        elif returnCode == 1:
            with row_lock:
                misc.utilities.acquire_lock(conn)
                cursor.execute("UPDATE tags SET running = '0' WHERE id = ?", (row_id,))
                conn.commit()
        elif returnCode is not None:
            misc.logger.log(f'Subprocess for tag "{tag}" was terminated with return code: {returnCode}')    
        else:
            misc.utilities.acquire_lock(conn)
            cursor.execute("UPDATE tags SET running = '0' WHERE id = ?", (row_id,))
            conn.commit()

finally:
    if row is not None:
        misc.utilities.acquire_lock(conn)
        cursor.execute("UPDATE tags SET running = '0' WHERE id = ?", (row_id,))
        conn.commit()
    db_utils.db_backup.manage_backups()

    conn.close()
    log_file.close()

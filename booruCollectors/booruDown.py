# downloader.py
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

import requests
import re
import config_utils
import sqlite3
import shutil
import os
import datetime
import time
import misc
from pathlib import Path
from itertools import repeat
import multiprocessing as mp

config = config_utils.config_loader.load_config()

if config:
    DATABASE_DB = (config['General']['database_db'])
    LOG_TXT = (config['General']['log_txt'])    
else:
    misc.logger.log('Configuration not loaded.')
    sys.exit()


def image_downloader(file_url, tag, dir_tag, initItems, ok_count, cpd_count, err_count, currItems):
    try:
        downInstead = 0

        conn = sqlite3.connect(DATABASE_DB, timeout=20)
        cursor = conn.cursor()

        imagePattern = re.compile(r"\/([^\/]+)$")
        urlPattern = re.compile(r"https?://(?:[^./]+\.)?([^./]+)\.[^/]+/")
        
        file_match = re.search(imagePattern, file_url)
        url_match = re.search(urlPattern, file_url)
        if file_match:
            file = file_match.group(1)
        if url_match:
            site = url_match.group(1)
            if site == 'rule34':
                rootPath = '/app/downloads/rule34/'
            elif site == 'gelbooru':
                rootPath = '/app/downloads/gelbooru/'
            elif site == 'donmai':
                site = "danbooru"
                rootPath = '/app/downloads/danbooru/'
                time.sleep(0.5)
            elif site == 'xbooru':
                rootPath = '/app/downloads/xbooru/'
            else:
                print("Site match failed for", file_url)    
        cursor.execute("SELECT EXISTS(SELECT 1 FROM {} WHERE file = ? LIMIT 1)".format(site), (file,))
        result = cursor.fetchone()[0]     
        if result == 0:
            try:
                destination = rootPath + tag + file
                response = requests.get(file_url)
                with open(destination, 'wb') as f:
                    f.write(response.content)
                misc.utilities.acquire_lock(conn)
                cursor.execute("INSERT INTO {} (file, tags) VALUES (?, ?)".format(site), (file, dir_tag))
                conn.commit()
                ok_count.value += 1
                currItems.value += 1
                progress = str(currItems.value) + "/" + str(initItems)
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f'[{timestamp}] DOWNLOADED [Ok: {str(ok_count.value)} | Err: {str(err_count.value)} | Cpd: {str(cpd_count.value)}] [{progress}]: {file}')
            except Exception as e:
                conn.rollback()
                err_count.value += 1
                currItems.value += 1
                progress = str(currItems.value) + "/" + str(initItems)         
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')         
                print(f'[{timestamp}] ERROR: {e} [Ok: {str(ok_count.value)} | Err: {str(err_count.value)} | Cpd: {str(cpd_count.value)}] [{progress}]: {file}')

        elif result == 1:
            misc.utilities.acquire_lock(conn)
            cursor.execute("SELECT tags FROM {} WHERE file = ?".format(site), (file,))
            conn.commit()
            entry_tags = cursor.fetchone()
            sep_tags = entry_tags[0].split(',')
            source_path = rootPath + sep_tags[0] + "/" + file

            destination = rootPath + tag + file
            if source_path != destination and os.path.exists(source_path) and not os.path.exists(destination):
                    shutil.copyfile(source_path, destination)
            elif not os.path.exists(destination) and not os.path.exists(source_path):
                try:
                    response = requests.get(file_url)
                    with open(destination, 'wb') as f:
                        f.write(response.content)
                    shutil.copyfile(destination, source_path)
                    downInstead = 1
                    shutil.copyfile(destination, source_path)
                except Exception as e:
                    print("Error line 119:", e)
            if not dir_tag in sep_tags:
                add_tag = "," + dir_tag
                misc.utilities.acquire_lock(conn)
                cursor.execute("UPDATE {} SET tags = tags || ? WHERE file = ?".format(site), (add_tag, file))
                conn.commit()
            if downInstead == 0:
                cpd_count.value += 1
                currItems.value += 1
                progress = str(currItems.value) + "/" + str(initItems)     
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')              
                print(f'[{timestamp}] INHERITED [Ok: {str(ok_count.value)} | Err: {str(err_count.value)} | Cpd: {str(cpd_count.value)}] [{progress}]: {file}')
            elif downInstead == 1:
                ok_count.value += 1
                currItems.value += 1
                progress = str(currItems.value) + "/" + str(initItems)
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f'[{timestamp}] DOWNLOADED [Ok: {str(ok_count.value)} | Err: {str(err_count.value)} | Cpd: {str(cpd_count.value)}] [{progress}]: {file}')
        else:
            err_count.value += 1
            currItems.value += 1
            progress = str(currItems.value) + "/" + str(initItems)  
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')                
            print(f'[{timestamp}] ERROR [Ok: {str(ok_count.value)} | Err: {str(err_count.value)} | Cpd: {str(cpd_count.value)}] [{progress}]: {file}')
    except Exception as e:
        misc.logger.log(f'Process for image "{file_url}" failed with error: {e}')
        conn.rollback()


        

def downloader(downloadList, downTag, threads: int = 6, delay: int = 0) -> None:
    manager = mp.Manager()
    ok_count = manager.Value('i', 0)
    cpd_count = manager.Value('i', 0)
    err_count = manager.Value('i', 0)
    currItems = manager.Value('i', 0)

    log_file = open(LOG_TXT, 'a')
    tag = "~".join(downTag)
    chars_to_replace = ['/', '<', '>', ':', '"', "\\", '|', '?', '*', '-', '(', ')']
    replacement_char = ''
    for char in chars_to_replace:
        tag = tag.replace(char, replacement_char)
    chars_to_replace = ['~', '_']
    replacement_char = '-'
    for char in chars_to_replace:
        tag = tag.replace(char, replacement_char)

    dir_tag = tag
    tag = tag + "/"
    initItems = len(downloadList)
    start_time = time.time()
    pool = mp.Pool(threads)
    pool.starmap(image_downloader, zip(downloadList, repeat(tag), repeat(dir_tag), repeat(initItems), repeat(ok_count), repeat(cpd_count), repeat(err_count), repeat(currItems)))
    end_time = time.time()
    misc.logger.log(f'Finished {tag} in {time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))}')
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
from pathlib import Path
from nhentai import utils
from itertools import repeat
import multiprocessing as mp
import time
import config_utils
import sqlite3
import misc
import json
import os


def album_page_query(album_id):
    config = config_utils.config_loader.load_config()
    if config:
        DATABASE_DB = (config['General']['database_db'])
        LOG_TXT = (config['General']['log_txt'])  
        cookies = (config['Nhentai']['cookies'])  
        USER_AGENT = (config['Nhentai']['user_agent'])  
    else:
        misc.logger.log('Configuration not loaded.')
        sys.exit()
    cookies = json.loads(cookies)
    headers = {'User-Agent': USER_AGENT}

    query = f'https://nhentai.net/api/gallery/{album_id}'
    response = requests.get(query, headers=headers, cookies=cookies)
    data = response.json()
    data = data['images']
    i = 1
    pages = []
    for page in data['pages']:
        pages.append((i, page['t']))
        i+=1
    return pages

def page_downloader(album_id: str, page: str, name: str, tag: str, media_id: str, album_folder:str, base_path: Path = '/app/downloads/nhentai', retries: int = 5):
    config = config_utils.config_loader.load_config()
    if config:
        DATABASE_DB = (config['General']['database_db'])
        LOG_TXT = (config['General']['log_txt'])  
        cookies = (config['Nhentai']['cookies'])  
        USER_AGENT = (config['Nhentai']['user_agent'])  
    else:
        misc.logger.log('Configuration not loaded.')
        sys.exit()
    cookies = json.loads(cookies)
    headers = {'User-Agent': USER_AGENT}    
    page_num = str(page[0])
    if page[1] == 'j':
        ext = '.jpg'
    elif page[1] == 'p':
        ext = '.png'
    elif page[1] == 'g':
        ext = '.gif'
    else:
        print(f'Page {page_num} unrecongnized ext: {page[1]}')
        return
    file_name = str(page_num) + str(ext)
    query = f'https://i.nhentai.net/galleries/{media_id}/{file_name}'
    base_path = Path(base_path)
    file_path = Path.joinpath(base_path, tag, album_folder, file_name)
    try:
        if not Path.exists(file_path):  
            print(f'Starting download of {album_folder} / {file_name}.')
            retry = 0
            response = requests.get(query, stream=True, timeout=30, headers=headers, cookies=cookies)              
            while response.status_code != 200 and retry <= retries:
                response = requests.get(query, stream=True, timeout=30, headers=headers, cookies=cookies)
                retry += 1
            if retry > retries:
                print(f'[ERROR] Retries reached for {file_name}.')
                return
            if len(response.content) > 0:
                with file_path.open('wb') as image:
                    image.write(response.content)
                    print(f'Download of {file_name} completed.')
    except Exception as e:
        print(f'[ERROR] Download for {file_name} failed: {e}')

def album_downloader(album_id: str, media_id: str, name:str, tag: str, threads: int = 4, delay: int = 0):
    config = config_utils.config_loader.load_config()
    if config:
        DATABASE_DB = (config['General']['database_db'])
        LOG_TXT = (config['General']['log_txt'])      
    else:
        misc.logger.log('Configuration not loaded.')
        sys.exit()

    conn = sqlite3.connect(DATABASE_DB, timeout=20)
    cursor = conn.cursor()
    try:
        pages = album_page_query(album_id)
    except Exception as e:
        print(f'Failed to grab info for {name}.')
        return
    album_id = str(album_id)
    album_folder = '[' + album_id + '] ' + name
    album_folder = str(album_folder)
    while len(album_folder) > 172:
        album_folder = album_folder[:-1]   
    album_folder = Path(album_folder)    
    misc.utilities.acquire_lock(conn)
    cursor.execute("SELECT EXISTS(SELECT 1 FROM nhentai WHERE album_id = ? LIMIT 1)", (album_id,))  
    conn.commit()
    result = cursor.fetchone()[0] 
    utils.create_folder(tag, album_folder)
    if result == 0:
        start_time = time.time()
        print(f'Starting doujin {name} with a total of {len(pages)} pages.')
        pool = mp.Pool(threads)
        pool.starmap(page_downloader, zip(repeat(album_id), pages, repeat(name), repeat(tag), repeat(media_id), repeat(album_folder)))
        end_time = time.time()
        print(f'Finished {name} in {time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))}')
        misc.utilities.acquire_lock(conn)
        cursor.execute("INSERT INTO nhentai (album_id, tags) VALUES (?, ?)", (album_id, tag))
        conn.commit()
    elif result == 1:
        misc.utilities.acquire_lock(conn)
        cursor.execute("SELECT tags FROM nhentai WHERE album_id = ?", (album_id,))
        conn.commit()
        album_tags = cursor.fetchone()
        sep_tags = album_tags[0].split(',')
        source_path = '/app/downloads/nhentai/' + sep_tags[0] + "/" + str(album_folder)
        link_path = '/app/downloads/nhentai/' + tag + "/" + str(album_folder)
        if source_path != link_path:
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    source_dir = os.path.join(root, file)
                    target_dir = os.path.join(link_path, file)
                    os.link(source_dir, target_dir)
        add_tag = "," + tag
        misc.utilities.acquire_lock(conn)
        cursor.execute("UPDATE nhentai SET tags = tags || ? WHERE album_id = ?", (add_tag, album_id))
        conn.commit()
        print(f'Linked {name} from {sep_tags[0]}.')

    if delay:
        time.sleep(delay)   
    return 0 

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
import manifest
import config_loader
import sqlite3
import shutil
import os
from logger import log
import datetime

config = config_loader.load_config()

if config:
    DATABASE_DB = (config['Manifest']['database_db'])
    LOG_TXT = (config['Manifest']['log_txt'])    
else:
    log('Configuration not loaded.')
    sys.exit()


def downloader(downloadList, downTag):
    e = "Couldn't possibly be a failure code"

    try:
        e = "Couldn't possibly be a failure code"

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
        currItems = 0
        ok_count = 0
        err_count = 0
        cpd_count = 0
        conn = sqlite3.connect(DATABASE_DB)
        cursor = conn.cursor()
        imagePattern = re.compile(r"\/images\/\d+\/([a-f0-9]+.*)")
        urlPattern = re.compile(r"https?://(?:[^./]+\.)?([^./]+)\.[^/]+/")

        for file_url in downloadList:
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
            cursor.execute("SELECT EXISTS(SELECT 1 FROM {} WHERE file = ? LIMIT 1)".format(site), (file,))
            result = cursor.fetchone()[0]     
            if result == 0:
                try:
                    destination = rootPath + tag + file
                    response = requests.get(file_url)
                    with open(destination, 'wb') as f:
                        f.write(response.content)
                    conn.execute('BEGIN TRANSACTION') 
                    cursor.execute("INSERT INTO {} (file, tags) VALUES (?, ?)".format(site), (file, dir_tag))
                    conn.commit()
                    ok_count = ok_count + 1
                    currItems = currItems + 1
                    progress = str(currItems) + "/" + str(initItems)
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f'[{timestamp}] DOWNLOADED [Ok: {str(ok_count)} | Err: {str(err_count)} | Cpd: {str(cpd_count)}] [{progress}]: {file}')
                except Exception as e:
                    conn.rollback()
                    err_count = err_count + 1
                    currItems = currItems + 1
                    progress = str(currItems) + "/" + str(initItems)         
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')         
                    print(f'[{timestamp}] ERROR: {e} [Ok: {str(ok_count)} | Err: {str(err_count)} | Cpd: {str(cpd_count)}] [{progress}]: {file}')

            elif result == 1:
                cursor.execute("SELECT tags FROM {} WHERE file = ?".format(site), (file,))
                entry_tags = cursor.fetchone()
                sep_tags = entry_tags[0].split(',')
                source_path = rootPath + sep_tags[0] + "/" + file

                destination = rootPath + tag + file
                if not source_path == destination:
                        shutil.copyfile(source_path, destination)
                if not dir_tag in sep_tags:
                    conn.execute('BEGIN TRANSACTION') 
                    add_tag = "," + dir_tag
                    cursor.execute("UPDATE {} SET tags = tags || ? WHERE file = ?".format(site), (add_tag, file))
                    conn.commit()
                cpd_count = cpd_count + 1
                currItems = currItems + 1
                progress = str(currItems) + "/" + str(initItems)     
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')              
                print(f'[{timestamp}] INHERITED [Ok: {str(ok_count)} | Err: {str(err_count)} | Cpd: {str(cpd_count)}] [{progress}]: {file}')
            else:
                err_count = err_count + 1
                currItems = currItems + 1
                progress = str(currItems) + "/" + str(initItems)  
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')                
                print(f'[{timestamp}] ERROR [Ok: {str(ok_count)} | Err: {str(err_count)} | Cpd: {str(cpd_count)}] [{progress}]: {file}')
    except Exception as e:
        log(f'Process for tag "{tag}" failed with error: {e}')
        conn.rollback()
    finally:
        if e == "Couldn't possibly be a failure code":
            print("Downloader Completed Successfully")
            return 0
        else:
            print("Downloader did an oopsie :(")
            return 1
        conn.close()


        


# downloader.py
#    luster
#    Copyright (C) 2023  MedicBehindYou
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

config = config_loader.load_config()

if config:
    DATABASE_DB = (config['Manifest']['database_db'])
    LOG_TXT = (config['Manifest']['log_txt'])    
else:
    log('Configuration not loaded.')
    sys.exit()


def downloader(downloadList, site, downTag):
    e = None
    try:
        if site == 'rule34':
            rootPath = '/app/downloads/rule34/'

        tag = "~".join(downTag)
        chars_to_replace = ['/', '<', '>', ':', '"', "\\", '|', '?', '*', '-', '(', ')']
        replacement_char = ''
        for char in chars_to_replace:
            tag = tag.replace(char, replacement_char)
        chars_to_replace = ['~', '_']
        replacement_char = '-'
        for char in chars_to_replace:
            tag = tag.replace(char, replacement_char)

        tag = tag + "/"
        tagPath = rootPath + tag
        if not os.path.exists(tagPath):
            os.makedirs(tagPath)

        initItems = len(downloadList)
        currItems = 0
        ok_count = 0
        err_count = 0
        cpd_count = 0


        conn = sqlite3.connect(DATABASE_DB)
        cursor = conn.cursor()

        for file_url in downloadList:
            pattern = r"\/images\/\d+\/([a-f0-9]+.*)"
            file_match = re.search(pattern, file_url)
            if file_match:
                file = file_match.group(1)
                cursor.execute("SELECT EXISTS(SELECT 1 FROM {} WHERE file = ? LIMIT 1)".format(site), (file,))
                result = cursor.fetchone()[0]     
                if result == 0:
                    try:
                        destination = rootPath + tag + file
                        
                        conn.commit()
                        response = requests.get(file_url)
                        with open(destination, 'wb') as f:
                            f.write(response.content) 
                        cursor.execute("INSERT INTO {} (file, path) VALUES (?, ?)".format(site), (file, destination))
                        conn.commit()
                        ok_count = ok_count + 1
                        currItems = currItems + 1
                        progress = str(currItems) + "/" + str(initItems)
                        print(f'DOWNLOADED [Ok: {str(ok_count)} | Err: {str(err_count)} | Cpd: {str(cpd_count)}] [{progress}]: {file}')
                    except Exception as e:
                        err_count = err_count + 1
                        currItems = currItems + 1
                        progress = str(currItems) + "/" + str(initItems)                  
                        print(f'ERROR: {e} [Ok: {str(ok_count)} | Err: {str(err_count)} | Cpd: {str(cpd_count)}] [{progress}]: {file}')

                elif result == 1:
                    cursor.execute("SELECT path FROM {} WHERE file = ?".format(site), (file,))
                    source_path = cursor.fetchone()[0]
                    destination = rootPath + tag + file
                    if not source_path == destination:
                        if not os.path.exists(destination):
                            shutil.copyfile(source_path, destination)
                    cpd_count = cpd_count + 1
                    currItems = currItems + 1
                    progress = str(currItems) + "/" + str(initItems)                   
                    print(f'INHERITED [Ok: {str(ok_count)} | Err: {str(err_count)} | Cpd: {str(cpd_count)}] [{progress}]: {file}')
                else:
                    err_count = err_count + 1
                    currItems = currItems + 1
                    progress = str(currItems) + "/" + str(initItems)                  
                    print(f'ERROR [Ok: {str(ok_count)} | Err: {str(err_count)} | Cpd: {str(cpd_count)}] [{progress}]: {file}')
    except Exception as e:
        log(f'Process for tag "{tag}" failed with error: {e}')
    finally:
        if e == None:
            return 0
        else:
            return 1
        conn.commit()
        conn.close()


        


# preskip.py
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

import config_loader
import sqlite3
import os
import re

config = config_loader.load_config()

if config:
    DATABASE_DB = (config['Manifest']['database_db'])
    LOG_TXT = (config['Manifest']['log_txt'])    
else:
    log('Configuration not loaded.')
    sys.exit()

def preskip(downloadList, site, downTag):
    if site == 'rule34':
        rootPath = '/app/downloads/rule34/'
    tag = "+".join(downTag)
    path = rootPath + tag + "/"
    print(downloadList)
    dupeFiles = []
    for file_url in downloadList:
        print("Checking", file_url)
        pattern = r"\/images\/\d+\/([a-f0-9]+.*)"
        file_match = re.search(pattern, file_url)
        if file_match:
            file = file_match.group(1)
            print(file)
            file_path = path + file
            print(file_path)
            if os.path.exists(file_path):
                dupeFiles.append(file_url)
                print("Pre-Skipping:", file_url)
            else:
                print("Does not exist:", file_path)
    for file_url in dupeFiles:
        downloadList.remove(file_url)

    print(downloadList)
    return downloadList
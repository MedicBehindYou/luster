# preskip.py
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

import config_loader
import sqlite3
import re

config = config_loader.load_config()

if config:
    DATABASE_DB = (config['Manifest']['database_db'])
    LOG_TXT = (config['Manifest']['log_txt'])    
else:
    log('Configuration not loaded.')
    sys.exit()

def preskip(downloadList, site, downTag):
    conn = sqlite3.connect(DATABASE_DB)
    cursor = conn.cursor()
    
    if site == 'rule34':
        rootPath = '/app/downloads/rule34/'
    elif site == 'gelbooru':
        rootPath = '/app/downloads/gelbooru/'
    tag = "+".join(downTag)

    tag = "~".join(downTag)
    chars_to_replace = ['/', '<', '>', ':', '"', "\\", '|', '?', '*', '-', '(', ')']
    replacement_char = ''
    for char in chars_to_replace:
        tag = tag.replace(char, replacement_char)
    chars_to_replace = ['~', '_']
    replacement_char = '-'
    for char in chars_to_replace:
        tag = tag.replace(char, replacement_char)
    
    dupeFiles = []
    pattern = re.compile(r"\/images\/\d+\/([a-f0-9]+.*)")
    initItems = len(downloadList)
    print("Intial list count is", initItems, ", starting preskip.")
    for file_url in downloadList:

        file_match = re.search(pattern, file_url)
        if file_match:
            file = file_match.group(1)

            cursor.execute("SELECT EXISTS(SELECT 1 FROM {} WHERE file = ? LIMIT 1)".format(site), (file,))
            result = cursor.fetchone()[0]
            cursor.execute("SELECT tags FROM {} WHERE file = ?".format(site), (file,))
            existing_tags = cursor.fetchone()
            
            if existing_tags:
                sep_tags = existing_tags[0].split(',')
                if result == 1 and tag in sep_tags:
                    dupeFiles.append(file_url)
            
    for file_url in dupeFiles:
        downloadList.remove(file_url)
    finalItems = len(downloadList)
    skipped = initItems - finalItems
    print("Preskipped", skipped, "items out of", initItems)

    return downloadList
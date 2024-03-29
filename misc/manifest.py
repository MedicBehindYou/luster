# manifest.py
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

import config_utils
import os
import sqlite3
import datetime
import sys
import misc


config = config_utils.config_loader.load_config()


if config:
    DATABASE_DB = (config['General']['database_db'])
    LOG_TXT = (config['General']['log_txt'])    
else:
    misc.logger.log('Configuration not loaded.')
    sys.exit()

def collector(DIRECTORY):
    files_list = []
    for root, dirs, files in os.walk(DIRECTORY):
        for file in files:
            files_list.append(os.path.join(root, file))
    return files_list

def file_insert(files_list, DATABASE_DB, site):
    conn = sqlite3.connect(DATABASE_DB, timeout=20)
    cursor = conn.cursor()
    complete = 0 
    iterNum = 0
    iterCount = 0
    fileNum = len(files_list)
    print("Processing", fileNum, "files.")

    try:
        for file in files_list:
            if iterNum == 0 and not conn.in_transaction:
                conn.execute('BEGIN TRANSACTION') 
            file_name = os.path.basename(file)
            dir_path = os.path.dirname(file)
            tag = os.path.basename(dir_path)

            cursor.execute("SELECT EXISTS(SELECT 1 FROM {} WHERE file = ? LIMIT 1)".format(site), (file_name,))
            result = cursor.fetchone()[0]
            cursor.execute("SELECT tags FROM {} WHERE file = ?".format(site), (file_name,))
            existing_tags = cursor.fetchone()
            
            if result == 0:
                cursor.execute("INSERT INTO {} (file, tags) VALUES (?, ?)".format(site), (file_name, tag))
                complete = complete + 1
                iterNum = iterNum + 1
                if iterNum == 10000:
                    iterNum = 0
                    iterCount = iterCount + 1
                    iterPrint = iterCount * 10000
                    print("Processed: ", iterPrint)
                    conn.commit()
            if existing_tags:
                sep_tags = existing_tags[0].split(',')
                if result == 1 and tag not in sep_tags:
                    add_tag = "," + tag
                    cursor.execute("UPDATE {} SET tags = tags || ? WHERE file = ?".format(site), (add_tag, file_name))
                    complete = complete + 1
                    iterNum = iterNum + 1
                    if iterNum == 10000:
                        iterNum = 0
                        iterCount = iterCount + 1
                        iterPrint = iterCount * 10000
                        print("Processed: ", iterPrint)                       
                        conn.commit()
    except Exception as e:
        print("error: ", e)
        conn.rollback()
    finally:
        print("Processed", complete, "entries.")
        conn.commit()
        conn.close()


def collect(site, DATABASE_DB):
    if site == "rule34":
        DIRECTORY = "/app/downloads/rule34"
    elif site == "gelbooru":
        DIRECTORY = "/app/downloads/rule34"
    elif site == "danbooru":
        DIRECTORY = "/app/downloads/danbooru"
    else:
        print('Invalid site.')
        sys.exit()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("Creating list. Starting at: ", timestamp)
    files_list = collector(DIRECTORY)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("List created, starting insert. Starting at: ", timestamp)
    file_insert(files_list, DATABASE_DB, site)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("Finished at: ", timestamp)


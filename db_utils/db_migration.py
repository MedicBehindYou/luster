# db_migration.py
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


import sqlite3
import os
import misc
import config_utils
import sys
import db_utils

config = config_utils.config_loader.load_config()

if config:
    DATABASE_DB = (config['General']['database_db'])
else:
    misc.logger.log('Configuration not loaded.')
    sys.exit()

def has_version_table(DATABASE_DB):
    conn = sqlite3.connect(DATABASE_DB, timeout=20)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='version'")
    version_table_exists = cursor.fetchone() is not None

    cursor.close()
    conn.close()

    return version_table_exists

def current_version():
    conn = sqlite3.connect(DATABASE_DB, timeout=20)
    cursor = conn.cursor()

    cursor.execute("SELECT version FROM version WHERE id = 1")
    version = cursor.fetchone()[0]
    return version

def migrate():
    try:
        if not has_version_table(DATABASE_DB):
            db_utils.db_backup.create_backup()
            misc.logger.log(f'Creating new versions table: {DATABASE_DB}')

            conn = sqlite3.connect(DATABASE_DB, timeout=20)
            cursor = conn.cursor()


            cursor.execute('''
                CREATE TABLE version (
                    id INTEGER PRIMARY KEY,
                    version TEXT
                )
            ''')


            cursor.execute("INSERT INTO version (version) VALUES ('0.0.0')")


            conn.commit()
            conn.close()

    except Exception as e:
        misc.logger.log('DB Version Detection Error: ', e)
        conn.close()
        sys.exit()

    try:
        conn = sqlite3.connect(DATABASE_DB, timeout=20)
        cursor = conn.cursor()
        # Execute a query to select the version from the version table
        cursor.execute("SELECT version FROM version WHERE id = 1")

        version = cursor.fetchone()[0]

        if version == "0.0.0":
            db_utils.db_backup.create_backup()
            cursor.execute('''ALTER TABLE tags ADD COLUMN running INTEGER DEFAULT 0''')
            cursor.execute("UPDATE version SET version = ('1.0.0') WHERE id = 1")

            conn.commit()
            version = "1.0.0"
            misc.logger.log('DB upgraded from 0.0.0 to 1.0.0')
        if version == "1.0.0":
            db_utils.db_backup.create_backup()
            cursor.execute('''CREATE TABLE IF NOT EXISTS rule34 (file TEXT UNIQUE, tags TEXT);''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_file ON rule34 (file);''')
            cursor.execute('''ALTER TABLE tags ADD COLUMN site INTEGER DEFAULT 0''')
            cursor.execute("UPDATE version SET version = ('2.0.0') WHERE id = 1")

            version = "2.0.0"
            conn.commit()
            misc.logger.log('DB upgraded from 1.0.0 to 2.0.0')
        if version == "2.0.0":
            db_utils.db_backup.create_backup()
            cursor.execute('DROP INDEX IF EXISTS idx_file')
            cursor.execute('''CREATE INDEX IF NOT EXISTS rule34_idx_file ON rule34 (file);''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS gelbooru (file TEXT UNIQUE, tags TEXT);''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS gelbooru_idx_file ON gelbooru (file);''')
            cursor.execute("UPDATE version SET version = ('2.1.0') WHERE id = 1")     

            version = "2.1.0"
            conn.commit()
            misc.logger.log('DB upgraded from 2.0.0 to 2.1.0')
        if version == "2.1.0":
            db_utils.db_backup.create_backup()
            cursor.execute('''CREATE TABLE IF NOT EXISTS danbooru (file TEXT UNIQUE, tags TEXT);''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS danbooru_idx_file ON gelbooru (file);''')
            cursor.execute("UPDATE version SET version = ('2.2.0') WHERE id = 1")     

            version = "2.2.0"
            conn.commit()
            misc.logger.log('DB upgraded from 2.1.0 to 2.2.0')  
        if version == "2.2.0":
            db_utils.db_backup.create_backup()
            cursor.execute('''ALTER TABLE tags ADD COLUMN genre TEXT DEFAULT 0''')
            cursor.execute("UPDATE version SET version = ('2.3.0') WHERE id = 1")     

            version = "2.3.0"
            conn.commit()
            misc.logger.log('DB upgraded from 2.2.0 to 2.3.0')  
        if version == "2.3.0":
            db_utils.db_backup.create_backup()
            cursor.execute('''CREATE TABLE IF NOT EXISTS nhentai (album_id TEXT UNIQUE, tags TEXT);''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS nhentai_idx_album_id ON nhentai (album_id);''')
            cursor.execute("UPDATE version SET version = ('2.4.0') WHERE id = 1") 

            version = "2.4.0"
            conn.commit()
            misc.logger.log('DB upgraded from 2.3.0 to 2.4.0')   
        if version == "2.4.0":
            db_utils.db_backup.create_backup()
            cursor.execute('''CREATE TABLE IF NOT EXISTS xbooru (file TEXT UNIQUE, tags TEXT);''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS xbooru_idx_file ON xbooru (file);''')
            cursor.execute("UPDATE version SET version = ('2.5.0') WHERE id = 1")     

            version = "2.5.0"
            conn.commit()
            misc.logger.log('DB upgraded from 2.4.0 to 2.5.0')     
        if version == "2.5.0":
            db_utils.db_backup.create_backup()
            cursor.execute('''CREATE TABLE IF NOT EXISTS konachan (file TEXT UNIQUE, tags TEXT);''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS konachan_idx_file ON konachan (file);''')
            cursor.execute("UPDATE version SET version = ('2.6.0') WHERE id = 1")     

            version = "2.6.0"
            conn.commit()
            misc.logger.log('DB upgraded from 2.5.0 to 2.6.0')       
        if version == "2.6.0":
            db_utils.db_backup.create_backup()
            cursor.execute('''CREATE TABLE IF NOT EXISTS yandere (file TEXT UNIQUE, tags TEXT);''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS yandere_idx_file ON yandere (file);''')
            cursor.execute("UPDATE version SET version = ('2.7.0') WHERE id = 1")     

            version = "2.7.0"
            conn.commit()
            misc.logger.log('DB upgraded from 2.6.0 to 2.7.0')                                
        else:
            misc.logger.log('No available migrations.')
    except sqlite3.Error as e:
        misc.logger.log("Error reading data from SQLite table:", e)

    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
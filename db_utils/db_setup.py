# db_setup.py
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
import sys
import misc
import config_utils

config = config_utils.config_loader.load_config()

if config:
    DATABASE_DB = (config['General']['database_db'])
else:
    misc.logger.log('Configuration not loaded.')
    sys.exit()


def setup_database():
    try:

        conn = sqlite3.connect(DATABASE_DB, timeout=20)
        cursor = conn.cursor()


        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                complete INTEGER DEFAULT 0,
                date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')


        conn.commit()
        conn.close()

        misc.logger.log('Database setup completed.')
    except Exception as e:
        misc.logger.log(f'Error setting up the database: {e}')
        sys.exit(1)  

if __name__ == "__main__":
    setup_database()


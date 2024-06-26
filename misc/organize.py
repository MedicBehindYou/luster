# organize.py
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
import config_utils
import misc

config = config_utils.config_loader.load_config()

if config:
    DATABASE_DB = (config['General']['database_db'])
else:
    misc.logger.log('Configuration not loaded.')
    sys.exit()


def reorder_table(db_file):
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        misc.utilities.acquire_lock(conn)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "tags_new" (
            "id"	INTEGER,
            "name"	TEXT,
            "complete"	INTEGER DEFAULT 0,
            "date"	INTEGER,
            "running"	INTEGER DEFAULT 0,
            "site"	INTEGER DEFAULT 0,
            "genre"	TEXT DEFAULT 0,
            PRIMARY KEY("id" AUTOINCREMENT)
            )
        ''')

        cursor.execute('''
            INSERT INTO "tags_new" ("name", "complete", "date", "running", "site", "genre")
            SELECT "name", "complete", "date", "running", "site", "genre" FROM "tags"
            WHERE "name" NOT LIKE '%uncensored%'
            ORDER BY "name" ASC
        ''')

        cursor.execute('''
            INSERT INTO "tags_new" ("name", "complete", "date", "running", "site", "genre")
            SELECT "name", "complete", "date", "running", "site", "genre" FROM "tags"
            WHERE "name" LIKE '%uncensored%'
            ORDER BY "name" ASC
        ''')

        cursor.execute('DROP TABLE IF EXISTS "tags"')

        cursor.execute('ALTER TABLE "tags_new" RENAME TO "tags"')

        conn.commit()
        conn.close()

        misc.logger.log('Table "tags" reordered successfully.')

    except sqlite3.Error as e:
        misc.logger.log(f'Error reordering the table: {str(e)}')

if __name__ == "__main__":
    db_file = DATABASE_DB 
    reorder_table(db_file)

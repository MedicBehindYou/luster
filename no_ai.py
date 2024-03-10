# no_ai.py
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
import datetime
import sys
import config_loader
from logger import log

config = config_loader.load_config()
if config:
    DATABASE_DB = config['No_AI']['database_db']
else:
    log('Configuration not loaded.')
    sys.exit()

def no_ai(DATABASE_DB):

    conn = sqlite3.connect(DATABASE_DB, timeout=5)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM tags")
    tags = cursor.fetchall()

    unique_tags = set()
    tags_with_no_ai = set()

    for row in tags:
        tag = row[0]
        if '-ai_generated' in tag:
            sep = tag.split(',')
            sep.remove('-ai_generated')
            normalized_tag = ','.join(sep)
            tags_with_no_ai.add(normalized_tag)
        else:
            unique_tags.add(tag)


    unique_tags -= tags_with_no_ai

    for tag in unique_tags:
        new_tag = tag + ',-ai_generated'
        cursor.execute("INSERT INTO tags (name) VALUES (?)", (new_tag,))

    conn.commit()

    conn.close()

    log('Unique tags without \',-ai_generated\' suffix added to the database.')

if __name__ == "__main__":
    no_ai(DATABASE_DB)
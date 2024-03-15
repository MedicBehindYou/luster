# importer.py
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
from datetime import datetime
from logger import log  
import config_loader

config = config_loader.load_config()

if config:
    DATABASE_DB = (config['General']['database_db'])
    ENTRIES_TXT = (config['Import']['entries_txt'])
else:
    log('Configuration not loaded.')
    sys.exit()

def bulk_import_tags(filename):
    try:

        conn = sqlite3.connect(DATABASE_DB, timeout=5)
        cursor = conn.cursor()


        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().replace('"', '').split('|')
                
                tag = parts[0].strip()
                if len(parts) > 1:
                    site = int(parts[1].strip())
                else:
                    site = 0
                cursor.execute("INSERT INTO tags (name, date, site) VALUES (?, ?, ?)", (tag, 'N/A', site))


        conn.commit()
        conn.close()

        log(f'Entries from "{filename}" imported successfully.')
    except Exception as e:
        log(f'Error bulk importing entries from "{filename}": {e}')

def single_import(name, siteNum: int = 0):
    try:

        conn = sqlite3.connect(DATABASE_DB, timeout=5)
        cursor = conn.cursor()


        sanitized_name = name.strip().replace('"', '')  
        cursor.execute("INSERT INTO tags (name, date, site) VALUES (?, ?, ?)", (sanitized_name, 'N/A', siteNum))


        conn.commit()
        conn.close()

        log(f'Single entry "{sanitized_name}" with site "{siteNum}" imported successfully.')
    except Exception as e:
        log(f'Error importing single entry "{name}": {e}')
    return

if __name__ == "__main__":
    import_tags(ENTRIES_TXT)

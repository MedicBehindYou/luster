# db_backup.py
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

import os
import shutil
import time
from logger import log 
import config_loader

config = config_loader.load_config()

if config:
    BACKUP_DIR = (config['Backup']['backup_dir'])
    DATABASE_DB = (config['General']['database_db'])
    BACKUP_RETENTION = int(config['Backup']['backup_retention'])
else:
    log('Configuration not loaded.')
    sys.exit()

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def create_backup():
    try:
        backup_file = f'{BACKUP_DIR}backup_{int(time.time())}.db'
        
        shutil.copy(DATABASE_DB, backup_file)
        
        log(f'Database backed up to {backup_file}')
    except Exception as e:
        log(f'Error creating database backup: {e}')

def manage_backups():
    try:
        backups = [os.path.join(BACKUP_DIR, file) for file in os.listdir(BACKUP_DIR) if file.startswith('backup_')]
        
        backups.sort(key=lambda x: os.path.getmtime(x))
        
        if len(backups) >= BACKUP_RETENTION:
            os.remove(backups[0])
            log(f'Oldest backup deleted: {backups[0]}')
        

        create_backup()
    except Exception as e:
        log(f'Error managing backups: {e}')

if __name__ == "__main__":
    create_backup() 
    manage_backups() 

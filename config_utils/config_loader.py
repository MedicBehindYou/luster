# config_loader.py
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

import configparser

def add_version():
    prepend_key = "[Version]\nversion = 0.0.0\n\n"
    with open("/config/config.ini", "r") as file:
        original_config = file.read()
    new_config = prepend_key + original_config
    with open("/config/config.ini", "w") as file:
        file.write(new_config)
    print('Added version key to config.ini')

def check_config_entry(config, section, key):
    if section in config and key in config[section]:
        return True
    else:
        return False

def load_config(config_file='/config/config.ini'):
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        return config
    except Exception as e:
        error_message = f'Error loading config: {e}'
        print(error_message)
        return None

def create_config():
    config = configparser.ConfigParser()

    # General Section
    config['General'] = {
        'database_db': '/config/database.db',
        'log_txt': '/config/log.txt'
    }

    # Main Section
    config['Main'] = {
        'max_inactivity_time': '6000'
    }

    # Backup Section
    config['Backup'] = {
        'backup_dir': '/config/backup/',
        'database_db': '/config/database.db',
        'backup_retention': '10'
    }

    # Import Section
    config['Import'] = {
        'entries_txt': '/config/entries.txt'
    }

    # Logger Section
    config['Logger'] = {
        'log_size': '1048576'
    }

    with open('/config/config.ini', 'w') as configfile:
        config.write(configfile)


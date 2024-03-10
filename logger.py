# logger.py
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
import datetime
import config_loader
import sys

config = config_loader.load_config()

if config:
    LOG_TXT = (config['General']['log_txt'])
    LOG_SIZE = int(config['Logger']['log_size'])
else:
    log('Configuration not loaded.')
    sys.exit()

def log(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f'[{timestamp}] {message}\n'
    print(log_message, end='')

    # Check the current log file size
    if os.path.exists(LOG_TXT):
        current_size = os.path.getsize(LOG_TXT)
    else:
        current_size = 0

    # Truncate the log file if it exceeds the maximum size
    if current_size + len(log_message) > LOG_SIZE:
        truncate_log_file(current_size + len(log_message) - LOG_SIZE)

    # Write the log message to the file
    with open(LOG_TXT, 'a') as log_file:
        log_file.write(log_message)

def truncate_log_file(remaining_size):
    with open(LOG_TXT, 'r+') as log_file:
        lines = log_file.readlines()
        log_file.seek(0)
        
        # Keep the last 'n' lines where 'n' is determined by the remaining size
        log_file.writelines(lines[-remaining_size:])
        log_file.truncate()

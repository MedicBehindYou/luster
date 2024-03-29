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

import requests
import config_utils
import json
import time

def fetch_albums(tag: str, sort: str = 'all_time'):
    page = 1
    nhentai_IDs = []
    config = config_utils.config_loader.load_config()
    if config:
        DATABASE_DB = (config['General']['database_db'])
        LOG_TXT = (config['General']['log_txt'])  
        cookies = (config['Nhentai']['cookies'])  
        USER_AGENT = (config['Nhentai']['user_agent'])  
        max_page_cap = (config['Nhentai']['max_page_cap']) 
    else:
        misc.logger.log('Configuration not loaded.')
        sys.exit()
    cookies = json.loads(cookies)
    headers = {'User-Agent': USER_AGENT}
    retries = 5
    retry = 0
    errors = 0
    while True:
        try:
            query = f'https://nhentai.net/api/galleries/search?query={tag}&sort={sort}&page={page}'
            print(f'Looking for Albums on page {page}.')
            response = requests.get(query, headers=headers, cookies=cookies)
            while response.status_code != 200 and retry <= retries:
                time.sleep(2.5)
                response = requests.get(query, headers=headers, cookies=cookies)
                retry += 1
            if retry > retries:
                print('[ERROR] Retry Limit reached.')
                page += 1
                retry = 0
            else:
                data = response.json()
                max_pages = data['num_pages']
                if data['num_pages'] < page or data['result'] == []:
                    return nhentai_IDs
                for album in data['result']:
                    nhentai_IDs.append((album['title']['pretty'], album['id'], album['media_id']))
                    if int(max_page_cap) <= page:
                        print(f'User set max pages reached.')                      
                        return nhentai_IDs
                page += 1
        except Exception as e:
            print(f'[ERROR] Query {query} failed with exception: {e}')
            page += 1
            errors += 1
            if errors >= 20:
                print(f'[ERROR ]Reached Max Error Limit for {tag}')
                break
    return nhentai_IDs

import requests
import config_loader
import json

def fetch_albums(tag: str, sort: str = 'all_time'):
    page = 1
    nhentai_IDs = []
#    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
    config = config_loader.load_config()
    if config:
        DATABASE_DB = (config['General']['database_db'])
        LOG_TXT = (config['General']['log_txt'])  
        cookies = (config['Nhentai']['cookies'])  
        USER_AGENT = (config['Nhentai']['user_agent'])  
        max_page_cap = (config['Nhentai']['max_page_cap']) 
    else:
        log('Configuration not loaded.')
        sys.exit()
    cookies = json.loads(cookies)
    headers = {'User-Agent': USER_AGENT}
    while True:
        query = f'https://nhentai.net/api/galleries/search?query={tag}&sort={sort}&page={page}'
        print(f'Looking for Albums on page {page}.')
        response = requests.get(query, headers=headers, cookies=cookies)
        data = response.json()
        max_pages = data['num_pages']
        if data['num_pages'] > page or data['result'] == []:
            break
        for album in data['result']:
            nhentai_IDs.append((album['title']['pretty'], album['id'], album['media_id']))
            if int(max_page_cap) <= page:
                break
        page += 1
    return nhentai_IDs

from luscious import queries
import requests
import config_loader


def luscious_artist_album_ids(artist):
    print('Starting album collection for', artist)
    base_url = 'https://members.luscious.net/graphql/nobatch/?operationName=AlbumList'
    artistClean = artist
    chars_to_replace = [' ']
    replacement_char = '_'
    for char in chars_to_replace:
        artistClean = artistClean.replace(char, replacement_char)

    artist_query = '+artist:_' + artistClean
    ids = []
    page = 1
    config = config_loader.load_config()
    if config:
        COOKIE_NAME = (config['Luscious']['cookie_name'])
        COOKIE_VALUE = (config['Luscious']['cookie_value'])        
    cookies = {COOKIE_NAME: COOKIE_VALUE}
    while True:
        query = queries.artist_search_query(artist_query, page)
        page += 1
        response = requests.post(base_url, json=query, cookies=cookies)
        data = response.json()
        ids.extend([item['id'] for item in data['data']['album']['list']['items']])
        if not data['data']['album']['list']['info']['has_next_page']:
            break
    print("Found", len(ids), "album(s) for artist:", artist)
    return ids

def luscious_album_pictures(album_id):
    base_url = 'https://members.luscious.net/graphql/nobatch/?operationName=AlbumListOwnPictures'
    picture_url_list = []
    page = 1
    config = config_loader.load_config()
    if config:
        COOKIE_NAME = (config['Luscious']['cookie_name'])
        COOKIE_VALUE = (config['Luscious']['cookie_value'])        
    cookies = {COOKIE_NAME: COOKIE_VALUE}    
    while True:
        query = queries.album_list_pictures_query(album_id, page)
        page += 1
        response = requests.post(base_url, json=query, cookies=cookies)
        data = response.json()
        picture_url_list.extend([(picture['position'], picture['url_to_original']) for picture in data['data']['picture']['list']['items']])
        if not data['data']['picture']['list']['info']['has_next_page']:
            break
    return picture_url_list

def luscious_album_name(album_id):
    base_url = 'https://members.luscious.net/graphql/nobatch/?operationName=AlbumGet'
    query = queries.album_info_query(album_id)
    config = config_loader.load_config()
    if config:
        COOKIE_NAME = (config['Luscious']['cookie_name'])
        COOKIE_VALUE = (config['Luscious']['cookie_value'])        
    cookies = {COOKIE_NAME: COOKIE_VALUE}
    response = requests.post(base_url, json=query, cookies=cookies)
    data = response.json()
    album_info = data['data']['album']['get']
    title = album_info['title']
    return title


def luscious_tag_search(search_query: str, genre_ids: str = '', sorting: str = 'rating_all_time'):
    base_url = 'https://members.luscious.net/graphql/nobatch/?operationName=AlbumList'
    page = 1
    album_list = []
    album_type = 'all'
    config = config_loader.load_config()
    if config:
        COOKIE_NAME = (config['Luscious']['cookie_name'])
        COOKIE_VALUE = (config['Luscious']['cookie_value'])  
        MAX_PAGES = (config['Luscious']['max_pages'])      
    cookies = {COOKIE_NAME: COOKIE_VALUE}
    while True:
        query = queries.album_search_query(search_query, album_type, page, genre_ids)
        page += 1
        response = requests.post(base_url, json=query, cookies=cookies)
        data = response.json()       
        data = data['data']['album']['list']
        album_list.extend([id['id'] for id in data['items']])
        if not data['info']['has_next_page'] or data['info']['page'] == MAX_PAGES:
            break
    return album_list
# gelbooru.py
#    luster
#    Copyright (C) 2024 MedicBehindYou
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
import json
import os
import re
import time
from urllib.parse import quote

def collector(downTag):
    print("Starting Gelbooru Collector.")
    joined_tags = "+".join(downTag)
    baseURL = "https://gelbooru.com/index.php?page=dapi&s=post&q=index"
    page = 0
    site = "gelbooru"
    downloadList = []
    end = 0
    tag = "~".join(downTag)
    chars_to_replace = ['/', '<', '>', ':', '"', "\\", '|', '?', '*', '-', '(', ')']
    replacement_char = ''
    for char in chars_to_replace:
        tag = tag.replace(char, replacement_char)
    chars_to_replace = ['~', '_']
    replacement_char = '-'
    for char in chars_to_replace:
        tag = tag.replace(char, replacement_char)

    dir_tag = tag
    tag = tag + "/"
    tagPath = '/app/downloads/gelbooru/' + tag
    if not os.path.exists(tagPath):
        os.makedirs(tagPath)  
    pattern = re.compile("""{'@attributes': {'limit': 100, 'offset': .*, 'count': .*}}""")  
    endStat = 0
    while True:
        url = f"{baseURL}&tags={joined_tags}&pid={page}&json=1&limit=1000"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                end_match = re.search(pattern, str(data))
                if end_match != None:
                    endStat = end_match.group(1)
                posts = data.get("post", [])
                for post in posts:
                    file_url = post.get('file_url')
                    if file_url is not None:
                        downloadList.append(file_url)                
                if endStat != None and endStat != 0:
                    page = page + 1
                    print("Page", page, "is empty. Stopping Collection.")
                    end = 1
                    break 
            elif response.status_code == 429:
                time.sleep(20)
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    end_match = re.search(pattern, str(data))
                    if end_match != None:
                        endStat = end_match.group(1)
                    posts = data.get("post", [])
                    for post in posts:
                        file_url = post.get('file_url')
                        if file_url is not None:
                            downloadList.append(file_url)                
                    if endStat != None and endStat != 0:
                        page = page + 1
                        print("Page", page, "is empty. Stopping Collection.")
                        end = 1
                        break 
            else:
                print(f"Error: {response.status_code}, {response.text}")
        except Exception as e:
            if "Expecting value: line 1 column 1 (char 0)" in str(e):
                print("End of pages")
                end = 1
                break
            else:
                print(e)
                break
        finally:
            if end != 1:
                print("Found up to 100 posts on page", page, "of Gelbooru.")
                page = page + 1
    downloadList = list(filter(lambda x: x is not None, downloadList))
    return downloadList
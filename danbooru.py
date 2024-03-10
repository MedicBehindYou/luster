# danbooru.py
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
import json
import os
from urllib.parse import quote
import time

def danbooruC(downTag):
    downloadList = [] 
    end = 0               
    if len(downTag) > 2:
        print("Danbooru does not accept more than two tags, skipping.")
        return
        
    print("Starting Danbooru Collector.")
    joined_tags = "+".join(downTag)
    baseURL = "https://danbooru.donmai.us/posts.json?limit=1000"
    page = 1
    site = "danbooru"
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
    tagPath = '/app/downloads/danbooru/' + tag
    if not os.path.exists(tagPath):
        os.makedirs(tagPath)
    while True:
        time.sleep(1)
        url = f"{baseURL}&tags={joined_tags}&page={page}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if str(data) == '[]':
                    page = page + 1
                    print("Page", page, "is empty. Stopping Collection.")
                    end = 1
                    break                
                for post in data:
                    file_url = post.get('file_url')
                    downloadList.append(file_url)
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
                print("Found up to 200 posts on page", page, "of Danbooru.")
                page = page + 1 
    return downloadList
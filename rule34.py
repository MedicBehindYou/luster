# rule34.py
#    luster
#    Copyright (C) 2023  MedicBehindYou
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
from urllib.parse import quote

def rule34C(downTag):
    joined_tags = "+".join(downTag)
    baseURL = "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index"
    page = 0
    site = "rule34"
    downloadList = []
    end = 0
    while True:
        url = f"{baseURL}&tags={joined_tags}&pid={page}&json=1"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if str(data) == '[]':
                    print("End of pages")
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
                print(page)
                page = page + 1
    return downloadList

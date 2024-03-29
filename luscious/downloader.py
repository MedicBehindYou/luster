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

import time
from luscious import utils
from pathlib import Path
from itertools import repeat
import multiprocessing as mp
import requests

def luscious_download_pictures(picture_url: tuple, title, item: Path, folderType: Path, album_folder: Path, retries: int = 5, base_path: Path = '/app/downloads/luscious'):
    position, picture_url = picture_url
    picture_url = utils.normalize_url(picture_url)
    picture_name = picture_url.rsplit('/', 1)[1]
    position_str = str(position).zfill(5)
    picture_name = position_str + '-' + picture_name
    base_path = Path(base_path)
    picture_path = Path.joinpath(base_path, folderType, item, album_folder, picture_name)
    try:
        if not Path.exists(picture_path):
            print(f'Starting download of {picture_name}.')
            retry = 0
            response = requests.get(picture_url, stream=True, timeout=30)
            while response.status_code != 200 and retry <= retries:
                response = requests.get(picture_url, stream=True, timeout=30)
                retry += 1
            if retry > retries:
                print(f'[ERROR] Retries reached for {picture_name}.')
                return
            if len(response.content) > 0:
                with picture_path.open('wb') as image:
                    image.write(response.content)
                    print(f'Download of {picture_name} completed.')
    except Exception as e:
        print(f'[ERROR] Download for {picture_name} failed: {e}')


def download(title: str, picture_url_list: list[str], album_folder: Path, item: Path, folderType: Path, threads: int = 4, delay: int = 0) -> None:
    start_time = time.time()
    album_folder = str(album_folder)
    while len(album_folder) > 172:
        album_folder = album_folder[:-1]
    album_folder = Path(album_folder)
    utils.create_folder(folderType, album_folder, item)
    print(f'Starting album {title} with a total of {len(picture_url_list)} images.')
    pool = mp.Pool(threads)
    pool.starmap(luscious_download_pictures, zip(picture_url_list, repeat(title), repeat(item), repeat(folderType), repeat(album_folder)))
    end_time = time.time()
    print(f'Finished {title} in {time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))}')
    if delay:
        time.sleep(delay)
    return 0
import time
from luscious import utils
from pathlib import Path
from itertools import repeat
import multiprocessing as mp
import requests

def luscious_download_pictures(picture_url: str, title, item: Path, retries: int = 5, base_path: Path = '/app/downloads/luscious'):
    picture_url = utils.normalize_url(picture_url)
    picture_name = picture_url.rsplit('/', 1)[1]
    albumClean = utils.format_foldername(title)
    base_path = Path(base_path)
    picture_path = Path.joinpath(base_path, item, albumClean, picture_name)
    if not Path.exists(picture_path):
        retry = 1
        response = requests.get(picture_url, stream=True, timeout=30)
        while response.status_code != 200 and retry <= retries:
            response = requests.get(picture_url, stream=True, timeout=self.timeout)
            retry += 1
        if retry > retries:
            print(f'[ERROR] Retries reached for {picture_name}.')
            return
        if len(response.content) > 0:
            with picture_path.open('wb') as image:
                image.write(response.content)

def download(title: str, picture_url_list: list[str], album_folder: Path, item: Path, threads: int = 4, delay: int = 0) -> None:
    start_time = time.time()
    utils.create_folder(item, album_folder)
    print(f'Starting album {title} with a total of {len(picture_url_list)} images.')
    pool = mp.Pool(threads)
    pool.starmap(luscious_download_pictures, zip(picture_url_list, repeat(title), repeat(item)))
    end_time = time.time()
    print(f'Finished {title} in {time.strftime("%H:%M:%S", time.gmtime(end_time - start_time))}')
    if delay:
        time.sleep(delay)
    return '0'
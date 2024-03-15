import re
from pathlib import Path


def normalize_url(picture_url: str) -> str:
  if picture_url.startswith('//'):
    picture_url = picture_url.replace('//', '', 1)
  if not picture_url.startswith('http://') and not picture_url.startswith('https://'):
    picture_url = f'https://{picture_url}'
  return picture_url
  
def format_foldername(title) -> str:

  album_name = re.sub(r'[^\w\-_\. ]', '_', title)
  return album_name

def create_folder(directory: Path, item: Path, base_path: Path = '/app/downloads/luscious') -> None:
  base_path = Path(base_path)
  directory = Path.joinpath(base_path, directory, item)
  print(directory)
  if not Path.exists(directory):
    Path.mkdir(directory, parents=True, exist_ok=True)
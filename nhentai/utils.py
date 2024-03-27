import re
from pathlib import Path

def create_folder(tag: str, album_folder: str, base_path: Path = '/app/downloads/nhentai') -> None:
  base_path = Path(base_path)
  directory = Path.joinpath(base_path, tag, album_folder)
  if not Path.exists(directory):
    Path.mkdir(directory, parents=True, exist_ok=True)
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
  pattern = re.compile(r'[^a-zA-Z\s{}[\]_-]')
  album_name = re.sub(pattern, '', album_name)
  return album_name

def create_folder(folderType: Path, item: Path, directory: Path, base_path: Path = '/app/downloads/luscious') -> None:
  base_path = Path(base_path)
  directory = Path.joinpath(base_path, folderType, directory, item)
  print(directory)
  if not Path.exists(directory):
    Path.mkdir(directory, parents=True, exist_ok=True)
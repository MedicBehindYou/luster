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

def replace_version(old_version, new_version):
    file_path = '/config/config.ini'
    with open(file_path, 'r') as file:
        filedata = file.read()

    filedata = filedata.replace(old_version, new_version)

    with open(file_path, 'w') as file:
        file.write(filedata)

def update_config(CONFIG_VERSION):
    if CONFIG_VERSION == '0.0.0':
        newKeys = "\n[Luscious]\ngenre_ids = ''\nmax_pages = 5\ncookie_name = ''\ncookie_value = ''\n"
        path = '/config/config.ini'
        with open(path, "a") as file:
            file.write(newKeys)
        replace_version("version = 0.0.0", "version = 1.0.0")
        print('Config upgraded to 1.0.0')
        CONFIG_VERSION == '1.0.0'
    if CONFIG_VERSION == '1.0.0':
        newKeys = "\n[Nhentai]\ncookies = ''\nuser_agent = ''\nmax_page_cap = 10\n"
        path = '/config/config.ini'
        with open(path, "a") as file:
            file.write(newKeys)
        replace_version("version = 1.0.0", "version = 2.0.0")
        print('Config upgraded to 2.0.0')    
        CONFIG_VERSION == '2.0.0'    
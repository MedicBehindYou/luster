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

import sqlite3
import config_utils
import misc


def album_skip(nhentai_IDs, tag):
    config = config_utils.config_loader.load_config()
    if config:
        DATABASE_DB = (config['General']['database_db'])
        LOG_TXT = (config['General']['log_txt'])  
   
    else:
        misc.logger.log('Configuration not loaded.')
        sys.exit()

    conn = sqlite3.connect(DATABASE_DB, timeout=20)
    cursor = conn.cursor()
    dupeAlbums = []
    initItems = len(nhentai_IDs)
    for album_name, album_id, media_id in nhentai_IDs:
        misc.utilities.acquire_lock(conn)
        cursor.execute("SELECT EXISTS(SELECT 1 FROM nhentai WHERE album_id = ? LIMIT 1)", (album_id,))
        result = cursor.fetchone()[0]
        cursor.execute("SELECT tags FROM nhentai WHERE album_id = ?", (album_id,))
        conn.commit()
        existing_tags = cursor.fetchone()
        if existing_tags:
            sep_tags = existing_tags[0].split(',')
            if result == 1 and tag in sep_tags:
                dupeAlbums.append((album_name, album_id, media_id))
    for album in dupeAlbums:
        nhentai_IDs.remove(album)
    finalItems = len(nhentai_IDs)
    skipped = initItems - finalItems
    print("Preskipped", skipped, "items out of", initItems)
    return nhentai_IDs
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

FROM debian:latest

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3

RUN pip install -U pip numpy scipy matplotlib pandas seaborn configparser requests lxml langcodes[data] --break-system-packages

COPY . /app

RUN mkdir /config && mkdir /app/downloads

RUN chmod 777 /app/ -R && chmod 777 /config/ -R

ENTRYPOINT ["python3", "-u", "/app/main.py"]
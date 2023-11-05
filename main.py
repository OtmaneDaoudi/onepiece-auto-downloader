from __future__ import print_function
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import os
import sys
import requests
from bs4 import BeautifulSoup
import base64
import tqdm
from urllib import parse


# URL to the list of episodes
BASE_URL = "https://witanime.com/anime/one-piece/"

OUTPUT_DIR = f"{os.getenv('USERPROFILE')}\\Desktop\\"

# Download parts
CHUNKS = 20


def download_file(file_id: str) -> None:
    """ Download a file from google drive using it's ID """
    creds, _ = google.auth.default()

    # create drive api client
    service = build('drive', 'v3', credentials=creds)

    # Request the file's metadata from Google Drive.
    file_metadata = service.files().get(fileId=file_id, fields='size,name').execute()

    file_name = file_metadata['name']
    file_size = int(file_metadata['size'])

    print(f'{"Size(Mb):" :<10}{file_size / 1024 / 1024 :<8.2f}')
    print(f'{"Name:" :<10}{file_name}')

    request = service.files().get_media(fileId=file_id)
    with open(OUTPUT_DIR+f'{file_name}', 'wb') as file:
        downloader = MediaIoBaseDownload(
            file, request, chunksize=(file_size + 500) / CHUNKS)  # 500 is added to ensure the last chunk is the last
        for part in tqdm.tqdm(range(CHUNKS)):
            downloader.next_chunk()

if __name__ == "__main__":
    print("Sending request...")
    req = requests.get(BASE_URL)
    if req.status_code != 200:
        print("Error occured while requesting base URL")
        sys.exit(-1)

    print("Parsing HTML...")
    html = req.text
    soup = BeautifulSoup(html, "html5lib")
    episode = soup.findAll("div", {"class": "DivEpisodeContainer"})[-1].h3.a

    episode_name = episode.text
    episode_link = base64.b64decode(episode["onclick"][13:-2]).decode()
    print(f'{"Episode:" :<10}{episode_name}')

    req = requests.get(episode_link)
    soup = BeautifulSoup(req.text, 'html5lib')

    episode_date = soup.find('div', {"class": 'user-post-info'}).text.strip()
    print(f'{"Date:" :<10}{episode_date}')

    fhd_drive_link = base64.b64decode(soup.findAll(
        'ul', {"class": "quality-list"})[-1]('li')[1].a["data-url"]).decode()

    file_id = parse.parse_qs(parse.urlparse(fhd_drive_link).query)['id'][0]

    download_file(file_id)
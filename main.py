from __future__ import print_function
import io
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

import os
import sys
import requests
from bs4 import BeautifulSoup
import base64
import re

import tqdm


# URL to the list of episodes
BASE_URL = "https://witanime.com/anime/one-piece/"
# where the downloaded episode will be placed"
OUTPUT_DIR = f"{os.getenv('USERPROFILE')}\\Desktop\\"
CHUNKS = 20


def download_file(file_id):
    creds, _ = google.auth.default()

    # create drive api client
    service = build('drive', 'v3', credentials=creds)

    # Request the file's metadata from Google Drive.
    file_metadata = service.files().get(fileId=file_id, fields='size,name').execute()

    print(file_metadata)
    file_name = file_metadata['name']
    file_size = int(file_metadata['size'])

    # Create a request to download the file.
    request = service.files().get_media(fileId=file_id)
    with open(OUTPUT_DIR+f'{file_name}', 'wb') as file:
        downloader = MediaIoBaseDownload(
            file, request, chunksize=(file_size + 500) / CHUNKS) # 500 is added to ensure the last chunk is the last
        
        for part in tqdm.tqdm(range(CHUNKS)):
            _, done = downloader.next_chunk()


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

    print(f'Latest episode: {episode_name}')
    print(f'Link: {episode_link}')

    # prompt
    req = requests.get(episode_link)
    soup = BeautifulSoup(req.text, 'html5lib')

    fhd_drive_link = base64.b64decode(soup.findAll(
        'ul', {"class": "quality-list"})[-1]('li')[1].a["data-url"]).decode()

    file_id = re.findall("id=.*", fhd_drive_link)[0][3:]

    download_file("0B1MVW1mFO2zmX1dDb0ZTMzd1YW8")

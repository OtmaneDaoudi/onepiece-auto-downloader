import os
import sys
import requests
from bs4 import BeautifulSoup
import base64

# URL to the list of episodes
BASE_URL = "https://witanime.com/anime/one-piece/"
# where the downloaded episode will be placed"
OUTPUT_DIR = f"{os.getenv('USERPROFILE')}\\Desktop"

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

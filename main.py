# %%
import os
import json

from src.logger import log
from src.downloader import Downloader

if __name__ == '__main__':
	log.warning('\nStarting...')

	DOWNLOADS_LOCATION = './downloads'

	settings_file = './settings.json'
	if os.path.isfile(settings_file):
		with open(settings_file) as f:
			settings = json.load(f)
		url = settings['URL']
	else:
		url = input('Please input a URL.\n')

	downloader = Downloader(DOWNLOADS_LOCATION, url)
	downloader.download_playlists()

	log.warning('Done.')

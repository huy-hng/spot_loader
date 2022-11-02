import time
import os
import json

from src.logger import log
from src import downloader
from src import download_client
from src import file_handler

def get_url():
	settings_file = './settings.json'
	if os.path.isfile(settings_file):
		with open(settings_file) as f:
			settings = json.load(f)
		url = settings['URL']
	else:
		url = input('Please input a URL.\n')

	vpn = input('Are you using a VPN? [Y/N]\n')
	if vpn.lower() != 'y':
		return
	return url


DOWNLOADS_LOCATION = './downloads'
def setup(url):
	file_handler.set_downloads_location(DOWNLOADS_LOCATION)
	file_handler.create_playlist_folder('')
	file_handler.create_playlist_folder('All Songs')

	downloader.set_downloads_location(DOWNLOADS_LOCATION)
	download_client.parse_url(url)


def main():
	url = get_url()
	if url is None: return

	log.warning('\nStarting...')
	start = time.perf_counter()

	setup(url)
	downloader.download_playlists()

	end = time.perf_counter()
	log.warning(f'Done. Time taken: {end-start}')


if __name__ == '__main__':
	main()

# %%
import os
import json

from src.logger import log
from src.downloader import Downloader

DOWNLOADS_LOCATION = './downloads'

def main():
	log.warning('\nStarting...')


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

	extended_input = input('Download extended versions of the songs? [Y/N]\n')
	extended = False
	if extended_input.lower() == 'y':
		extended = True
		
	downloader = Downloader(DOWNLOADS_LOCATION, url)
	downloader.get_playlists()

	log.warning('Done.')


if __name__ == '__main__':
	main()

import time
import os
import json
import concurrent.futures

from src.logger import log
from src import downloader
from src import download_client
from src import file_handler
from src.tests import optimize_query, get_results

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


DOWNLOADS_LOCATION = './downloads'
def setup(url):
	file_handler.set_downloads_location(DOWNLOADS_LOCATION)
	file_handler.create_playlist_folder('')
	file_handler.create_playlist_folder('All Songs')

	downloader.set_downloads_location(DOWNLOADS_LOCATION)
	download_client.parse_url(url)


def download():
	log.warning('\nStarting...')
	start = time.perf_counter()

	downloader.download_playlists()

	end = time.perf_counter()
	log.warning(f'Done. Time taken: {end-start}')


def test():
	url = 'https://myfreemp3juices.cc/'
	playlist_url = 'https://open.spotify.com/playlist/0oWDXsY9BhT9NKimKwNY9d?si=bb79d60100714e1e'
	start = time.perf_counter()

	futures = optimize_query(url, playlist_url)
	get_results(futures)

	end = time.perf_counter()
	print(f'1 time taken: {end-start}')


def main():
	# url = get_url()
	url = 'https://myfreemp3juices.cc/'
	if url is None:
		return
	setup(url)
	download()


if __name__ == '__main__':
	# pass
	main()
	# test()


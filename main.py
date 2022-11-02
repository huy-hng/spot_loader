import time
import os
import json
import concurrent.futures

from src.logger import log
from src.downloader import Downloader
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


def save(obj):
    return (obj.__class__, obj.__dict__)


def restore(saved):
	print(saved)
	cls = saved[0]
	attributes = saved[1]
	obj = cls.__new__(cls)
	obj.__dict__.update(attributes)
	return obj

def run(saved, url):
	print(saved)
	# restored: Downloader = restore(saved)
	# restored.download_playlist(url)


def download(url):
	log.warning('\nStarting...')

	DOWNLOADS_LOCATION = './downloads'
	# DOWNLOADS_LOCATION = './downloads2'

	start = time.perf_counter()
	downloader = Downloader(DOWNLOADS_LOCATION, url)
	print(downloader.downloads_location)

	with open('./playlists.txt') as f:
		playlist_urls = [line.strip() for line in f.readlines()]

	log.info(f'Found {len(playlist_urls)} playlist.')

	# saved = save(downloader)
	# # restored = restore(saved)
	# with concurrent.futures.ProcessPoolExecutor(max_workers=16) as executor:
	# 	for res in executor.map(run, saved, playlist_urls):
	# 		print(res)

	downloader.download_playlists()

	# downloader.executor.shutdown(wait=True)
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
	download(url)


if __name__ == '__main__':
	# pass
	main()
	# test()


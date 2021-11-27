# %%
from src.logger import log
from src.downloader import Downloader
if __name__ == '__main__':
	log.warning('\nStarting...')

	DOWNLOADS_LOCATION = './downloads'
	url = input('Please input a URL.\n')
	downloader = Downloader(DOWNLOADS_LOCATION, url)
	downloader.download_playlists()

	log.warning('Done.')

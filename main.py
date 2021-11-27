# %%
from src.logger import log
from src.downloader import Downloader
if __name__ == '__main__':
	log.warning('\nStarting...')

	DOWNLOADS_LOCATION = './downloads'
	downloader = Downloader(DOWNLOADS_LOCATION)
	downloader.download_playlists()

	log.warning('Done.')

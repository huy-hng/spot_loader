import time
import os
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, ProcessPoolExecutor
import concurrent.futures

from requests import Response

from src.logger import log
from src.spotify import Spotipy
from src.download_client import DownloadClient
from src.file_handler import FileHandler
from src.song import MP3JuicesSongType


start = time.perf_counter()

class Downloader:
	def __init__(self, downloads_location: str, url: str):
		self.downloads_location = downloads_location

		self.sp = Spotipy()
		self.mp3 = DownloadClient(url)
		self.fh = FileHandler(downloads_location=downloads_location)

		self.fh.create_playlist_folder('')
		self.fh.create_playlist_folder('All Songs')


	def download_playlists(self):
		with open('./playlists.txt') as f:
			playlist_urls = [line.strip() for line in f.readlines()]
			playlist_urls = playlist_urls[1:5]

		log.info(f'Found {len(playlist_urls)} playlist.')

		# with ThreadPoolExecutor(max_workers=4) as executor:
		with ProcessPoolExecutor() as executor:
			executor.map(self.download_playlist, playlist_urls)
			# map(self.download_playlist, playlist_urls)
			# 	print(res)
			# for url in playlist_urls:
			# 	executor.submit(self.download_playlist, url)
				# self.download_playlist(url)


	def download_playlist(self, url: str):
		start = time.perf_counter()
		playlist_name = self.sp.get_playlist_name(url)
		log.info(f'Downloading Playlist: {playlist_name}')

		playlist_name = self.fh.normalize_name(playlist_name)
		self.fh.create_playlist_folder(playlist_name)

		tracks = self.sp.get_playlist_tracks(url)

		with ThreadPoolExecutor(max_workers=32) as executor:
			for i, track in enumerate(tracks):
				parsed_track = self.sp.parse_track(track)
				executor.submit(self.download_song, playlist_name, parsed_track, (i+1, len(tracks)))
				# self.download_song(playlist_name, parsed_track, (i+1, len(tracks)))

		end = time.perf_counter()
		log.info(f'{playlist_name} time taken: {end-start}')


	def download_song(self, playlist_name:str, track: dict, track_num: tuple[int, int]):
		query = f"{track['artists']} - {track['name']}"

		filename = get_filename(query)

		if self.alread_downloaded(filename):
			log.debug(f'"{query}" already downloaded.')
			self.fh.move_track(playlist_name, filename)
			return

		log.debug(f'Downloading "{query}"...')
		song = self.mp3.get_song(track, query)
		if song is None:
			return

		self.fh.write_song(filename, song)
		self.fh.move_track(playlist_name, filename)

		# album_cover = self.mp3.download_album_cover(song_info)
		album_cover = None
		dst = f'{self.downloads_location}/{playlist_name}/{filename}'
		self.fh.edit_file_metadata(dst, track_num, track, album_cover)


	def alread_downloaded(self, filename: str):
		path = f'{self.downloads_location}/All Songs/{filename}'
		if self.fh.is_file(path):
			return True
		return False


def get_filename(query: str):
	filename = f'{query}.mp3'
	filename = filename.replace('/', '_')
	return filename

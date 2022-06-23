import shutil
import os
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor
import concurrent.futures

from requests import Response

from src.logger import log
from src.spotify import Spotipy
from src.download_client import DownloadClient
from src.file_handler import FileHandler
from src.song import MP3JuicesSongType


class Downloader:
	def __init__(self, downloads_location: str, url: str):
		self.downloads_location = downloads_location

		self.sp = Spotipy()
		self.mp3 = DownloadClient(url)
		self.fh = FileHandler(downloads_location=downloads_location)

		self.fh.create_playlist_folder('')
		self.fh.create_playlist_folder('All Songs')

		self.executor = ThreadPoolExecutor()

			
	def download_playlists(self):
		with open('./playlists.txt') as f:
			playlists = [line.strip() for line in f.readlines()]

		log.info(f'Found {len(playlists)} playlists.')
		# tracks_in_playlists = {}

		# pairs = {}
		for url in playlists:
			playlist_name = self.sp.get_playlist_name(url)
			log.info(f'Downloading {playlist_name}')

			# track_list_future = self.executor.submit(self.download_playlist, url)
			# pairs[track_list_future] = playlist_name

			# log.debug(f'Tracklist of {playlist_name}')
			# log.debug(track_list)

			track_list = self.download_playlist(url)
			log.info(f'Playlist {playlist_name} finished downloading. Moving Tracks.')
			self.move_tracks_to_folder(playlist_name, track_list)


		# for future in concurrent.futures.as_completed(pairs):
		# 	playlist_name = pairs[future]
		# 	log.info(f'Playlist {playlist_name} finished downloading. Moving Tracks.')
		# 	track_list = future.result()
		# 	self.move_tracks_to_folder(playlist_name, track_list)

		

	def download_playlist(self, url: str):
		tracks = self.sp.get_playlist_tracks(url)

		track_list = []
		futures = []

		# log.info(f'Playlist has {len(tracks)} tracks in it.')
		for i, track in enumerate(tracks):
			query = self.sp.track_to_query(track)
			filename = f'{query}.mp3'
			filename = filename.replace('/', '')

			track_list.append(filename)

			future = self.executor.submit(self.download_song, track, (i+1, len(tracks)), filename)
			futures.append(future)
			# self.download_song(track, (i+1, len(tracks)), filename)

		concurrent.futures.wait(futures, return_when=ALL_COMPLETED)
		return track_list


	def download_song(self, track: dict, track_num: int, filename: str):
		duration = round(track['track']['duration_ms'] / 1000)
		query = self.sp.track_to_query(track)

		log.debug(f'Searching for "{query}"')
		song_info = self.mp3.find_song(query, duration)
		if song_info is None:
			return


		file_location = f'{self.downloads_location}/All Songs/{filename}'
		if self.is_file(file_location):
			log.debug(f'"{query}" already downloaded.')
			return

		log.info(f'Downloading "{query}"...')
		song = self.mp3.download_song(song_info)
		if song is None:
			return
		self.fh.write_song(filename, song)

		album_cover = self.mp3.download_album_cover(song_info)

		self.fh.edit_file_metadata(filename, track_num, track, song_info, album_cover)


	def move_tracks_to_folder(self, playlist_name: str, track_list: list[str]):
		playlist_name = self.fh.normalize_name(playlist_name)
		self.fh.create_playlist_folder(playlist_name)
		for track_name in track_list:
			src = f'{self.downloads_location}/All Songs/{track_name}'
			dst = f'{self.downloads_location}/{playlist_name}/{track_name}'

			if not self.is_file(src):
				continue

			if self.is_file(dst):
				continue

			shutil.copy2(src, dst)

	@staticmethod
	def is_file(file_location: str):
		return os.path.isfile(file_location)
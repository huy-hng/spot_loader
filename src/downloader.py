import shutil
import os
from concurrent.futures import Future, ThreadPoolExecutor

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

		self.fh.create_playlist_folder('All Songs')

			
	def get_playlists(self):
		with open('./playlists.txt') as f:
			playlists = [
				line.strip()
				for line in f.readlines()
				if line.startswith('https://open.spotify.com/playlist/')
			]

		log.info(f'Found {len(playlists)} playlists.')
		# tracks_in_playlists = {}
		for url in playlists:
			playlist_name = self.sp.get_playlist_name(url)
			playlist_name = self.fh.normalize_name(playlist_name)
			self.fh.create_playlist_folder(playlist_name)

			log.info(f'Downloading {playlist_name}')

			self.get_playlist(url, playlist_name)


	def get_playlist(self, url: str, playlist_name: str):
		tracks = self.sp.get_playlist_tracks(url)


		log.info(f'Playlist has {len(tracks)} tracks in it.')
		with ThreadPoolExecutor() as executor:
			for i, track in enumerate(tracks):
				future = executor.submit(self.get_song, playlist_name, track, (i+1, len(tracks)))
				future.add_done_callback(self.log_future_exception)

		self.fh.delete_old_songs_from_playlist(playlist_name, tracks)

	def log_future_exception(self, future: Future):
		ex = future.exception()
		if ex is not None:
			log.exception(ex)

	def get_song(self, playlist_name: str, track: dict, track_num: int):
		query = self.fh.track_to_query(track)
		log.debug(f'Searching for "{query}"')

		file_name = f'{self.fh.normalize_name(query)}.mp3'
		duration = round(track['track']['duration_ms'] / 1000)

		download_info = self.mp3.find_song(query, duration)
		if download_info is None:
			return

		download_path = f'{self.downloads_location}/All Songs/{file_name}'
		destination_path = f'{self.downloads_location}/{playlist_name}/{file_name}'


		if self.fh.is_file(download_path):
			album_cover = self.mp3.download_album_cover(download_info)
			self.fh.edit_file_metadata(destination_path, track_num, track, download_info, album_cover)
			
			if not self.fh.is_file(destination_path):
				self.fh.copy_track_to_folder(playlist_name, file_name)
				self.fh.edit_track_num(destination_path, track_num)
			# if duration == self.fh.get_track_duration(download_location):
			log.debug(f'"{query}" already downloaded.')
			return


		log.info(f'Downloading "{query}"...')
		song = self.mp3.download_song(download_info)
		if song is None:
			return

		self.fh.write_song(file_name, song)

		album_cover = self.mp3.download_album_cover(download_info)
		self.fh.edit_file_metadata(download_path, track_num, track, download_info, album_cover)

		self.fh.copy_track_to_folder(playlist_name, file_name)
		self.fh.edit_track_num(destination_path, track_num)

import shutil
import os
from concurrent.futures import ThreadPoolExecutor

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

			
	def download_playlists(self):
		with open('./playlists.txt') as f:
			playlists = [line.strip() for line in f.readlines()]

		log.info(f'Found {len(playlists)} playlists.')
		# tracks_in_playlists = {}
		for url in playlists:
			playlist_name = self.sp.get_playlist_name(url)
			log.info(f'Downloading {playlist_name}')

			track_list = self.download_playlist(url)

			# tracks_in_playlists[playlist_name] = track_list
			log.debug(f'Tracklist of {playlist_name}')
			log.debug(track_list)

			self.move_tracks_to_folder(playlist_name, track_list)
		

	def download_playlist(self, url: str):
		tracks = self.sp.get_playlist_tracks(url)

		track_list = []

		log.info(f'Playlist has {len(tracks)} tracks in it.')
		with ThreadPoolExecutor() as executor:
			for i, track in enumerate(tracks):
				# self.download_song(track, track_list)
				query = self.sp.track_to_query(track)
				filename = f'{query}.mp3'
				filename = filename.replace('/', '')

				track_list.append(filename)

				executor.submit(self.download_song, track, (i+1, len(tracks)), filename)
				# self.download_song(track, (i+1, len(tracks)), filename)

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

			shutil.copy2(src, dst)

	@staticmethod
	def is_file(file_location: str):
		return os.path.isfile(file_location)
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
		tracks_in_playlists = {}
		for url in playlists:
			playlist_name = self.sp.get_playlist_name(url)
			log.info(f'Downloading {playlist_name}')

			track_list = self.download_playlist(url)

			tracks_in_playlists[playlist_name] = track_list

			self.move_tracks_to_folder(playlist_name, track_list)
		

	def download_playlist(self, url: str):
		tracks = self.sp.get_playlist_tracks(url)

		track_list = []

		log.info(f'Playlist has {len(tracks)} tracks in it.')
		with ThreadPoolExecutor() as executor:
			for track in tracks:
				# self.download_song(track, track_list)
				executor.submit(self.download_song, track, track_list)

		return track_list


	def download_song(self, track, track_list: list):
		duration = round(track['track']['duration_ms'] / 1000)
		query = self.sp.track_to_query(track)

		log.debug(f'Searching for "{query}"')
		song_info: MP3JuicesSongType = self.mp3.find_song(query, duration)
		if song_info is None:
			log.error(f'{query} could not be found.')
			return

		# filename = self.fh.get_filename(song_info)
		filename = f'{query}.mp3'
		filename = filename.replace('/', '')
		track_list.append(filename)

		if os.path.isfile(f'{self.downloads_location}/All Songs/{filename}'):
			log.debug(f'"{query}" already downloaded.')
			return

		log.info(f'Downloading "{query}"...')
		song: Response = self.mp3.download_song(song_info)
		if song is None:
			return
		self.fh.write_song(filename, song)

		album_cover: Response = self.mp3.download_album_cover(song_info)
		self.fh.edit_file_metadata(song_info, album_cover)


	def move_tracks_to_folder(self, playlist_name: str, track_locations: list):
		self.fh.create_playlist_folder(playlist_name)
		for location in track_locations:
			src = f'{self.downloads_location}/All Songs/{location}'
			dst = f'{self.downloads_location}/{playlist_name}/{location}'
			shutil.copy2(src, dst)

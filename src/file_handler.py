import os

import requests
from requests import Response
import eyed3

from src.song import MP3JuicesSongType

class FileHandler:
	def __init__(self, playlist_name: str):
		self.playlist_name = playlist_name
		downloads_folder = f'./downloads/{self.playlist_name}'
		if not os.path.isdir(downloads_folder):
			os.mkdir(downloads_folder)


	def write_song(self, song: MP3JuicesSongType, res: Response):
		_, file_location = self.get_name_and_location(song)

		if os.path.isfile(file_location):
			# check if file already exists, if yes skip
			return

		with open(file_location, 'wb') as f:
			for chunk in res.iter_content(chunk_size=128):
				f.write(chunk)

		try:
			self.edit_file_metadata(song)
		except Exception as e:
			print(e)



	def edit_file_metadata(self, song: MP3JuicesSongType):
		filename, file_location = self.get_name_and_location(song)

		audiofile = eyed3.load(file_location)

		if audiofile is None:
			raise Exception(f"Coudn't change Meta Data of {filename}")

		audiofile.tag.artist = song['artist']
		audiofile.tag.title = song['title']

		audiofile.tag.save()


	def get_name_and_location(self, song: MP3JuicesSongType):
		filename = f"{song['artist']} - {song['title']}"
		location = f'./downloads/{self.playlist_name}/{filename}.mp3'
		return (filename, location)
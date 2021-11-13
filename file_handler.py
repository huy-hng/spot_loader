import os
import shutil

import requests
import eyed3

from song import MP3JuicesSongType

class FileHandler:
	def __init__(self, playlist_name: str):
		self.playlist_name = playlist_name


	def download_song(self, song: MP3JuicesSongType):
		artist = song['artist']
		title = song['title']

		filename = f'{artist} - {title}'
		file_location = f'./downloads/{self.playlist_name}/{filename}.mp3'

		if os.path.isfile(file_location):
			# check if file already exists, if yes skip
			return

		with requests.get(song['url'], stream=True) as r:
			if r.status_code == 404:
				print(f"Couldn't find {filename}")
				return

			with open(file_location, 'wb') as f:
				shutil.copyfileobj(r.raw, f)


	def edit_file_metadata(self):
		audiofile = eyed3.load(file_location)
		if audiofile is None:
			return print(f"Coudn't change Meta Data of {filename}")
		audiofile.tag.artist = artist
		audiofile.tag.title = title

		audiofile.tag.save()
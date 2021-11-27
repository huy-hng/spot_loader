import os

from requests import Response
import eyed3
from eyed3.id3.frames import ImageFrame
	
from src.song import MP3JuicesSongType

class FileHandler:
	def __init__(self, downloads_location='./downloads') -> None:
			self.downloads_location = downloads_location


	def create_playlist_folder(self, playlist_name: str):
		downloads_folder = f'{self.downloads_location}/{playlist_name}'
		if not os.path.isdir(downloads_folder):
			os.mkdir(downloads_folder)


	def write_song(self, filename: str, res: Response):
		file_location = f'{self.downloads_location}/All Songs/{filename}'

		with open(file_location, 'wb') as f:
			for chunk in res.iter_content(chunk_size=128):
				f.write(chunk)


	def edit_file_metadata(self, song: MP3JuicesSongType, album_cover: Response):
		filename = self.get_filename(song)

		audiofile = eyed3.load(f'{self.downloads_location}/All Songs/{filename}')

		if (audiofile.tag == None):
			audiofile.initTag()

		if audiofile is None:
			raise Exception(f"Coudn't change Meta Data of {filename}")

		audiofile.tag.artist = song['artist']
		audiofile.tag.title = song['title']
		audiofile.tag.album = song['album']['title']
		# audiofile.tag.

		if album_cover is not None:
			audiofile.tag.images.set(
				ImageFrame.FRONT_COVER,
				album_cover.content,
				'image/jpeg')

		audiofile.tag.save()


	def get_filename(self, song: MP3JuicesSongType):
		filename = f"{song['artist']} - {song['title']}.mp3"
		return filename

	# def get_file_location(self, filename: str):

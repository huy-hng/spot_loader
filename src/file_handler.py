import os

from requests import Response
import eyed3
from eyed3.id3.frames import ImageFrame
eyed3.log.setLevel("ERROR")

from src.logger import log
from src.song import MP3JuicesSongType

class FileHandler:
	def __init__(self, downloads_location='./downloads') -> None:
			self.downloads_location = downloads_location


	def normalize_name(self, name: str):
		return name.replace('/', '_')

	def create_playlist_folder(self, playlist_name: str):
		playlist_name = self.normalize_name(playlist_name)
		downloads_folder = f'{self.downloads_location}/{playlist_name}'
		if not os.path.isdir(downloads_folder):
			os.mkdir(downloads_folder)


	def write_song(self, filename: str, res: Response):
		filename = self.normalize_name(filename)
		file_location = f'{self.downloads_location}/All Songs/{filename}'

		try:
			with open(file_location, 'wb') as f:
				for chunk in res.iter_content(chunk_size=128):
					f.write(chunk)
		except Exception as e:
			log.exception(e)


	def edit_file_metadata(self, filename:str,
															 track_num: int,
															 track: dict,
															 song: MP3JuicesSongType,
															 album_cover: Response):

		filename = self.normalize_name(filename)
		audiofile = eyed3.load(f'{self.downloads_location}/All Songs/{filename}')

		if audiofile is None:
			log.error(f"Coudn't change Meta Data of {filename}")
			return

		if (audiofile.tag == None):
			audiofile.initTag()

		track = track['track']
		track_name = track['name']
		track_artist = track['artists'][0]['name']
		audiofile.tag.artist = track_artist
		audiofile.tag.title = track_name
		audiofile.tag.track_num = track_num

		if song.get('album') is not None:
			audiofile.tag.album = song['album']['title']

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

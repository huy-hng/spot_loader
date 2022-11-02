import shutil
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


	def move_track(self, playlist_name: str, track_filename: str):
		src = f'{self.downloads_location}/All Songs/{track_filename}'
		dst = f'{self.downloads_location}/{playlist_name}/{track_filename}'

		if self.is_file(src) and not self.is_file(dst):
			shutil.copy2(src, dst)


	def edit_file_metadata(self,
			file_path:str,
			track_num: tuple[int, int],
			track: dict,
			# song: MP3JuicesSongType,
			album_cover: Response | None):

		audiofile = eyed3.load(file_path)

		if audiofile is None:
			log.error(f"Coudn't change Meta Data of {file_path}")
			return

		if (audiofile.tag == None):
			audiofile.initTag()

		audiofile.tag.artist = track['artists']
		audiofile.tag.title = track['name']
		audiofile.tag.track_num = track_num
		audiofile.tag.album = track['album_name']

		if album_cover is not None:
			audiofile.tag.images.set(
				ImageFrame.FRONT_COVER,
				album_cover.content,
				'image/jpeg')

		audiofile.tag.save()


	@staticmethod
	def is_file(file_location: str):
		return os.path.isfile(file_location)

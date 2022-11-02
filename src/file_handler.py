from email.mime import audio
from fileinput import filename
import os
import glob
import shutil

from requests import Response
import eyed3
from eyed3.id3.frames import ImageFrame
eyed3.log.setLevel("ERROR")

from src.logger import log
from src.song import MP3JuicesSongType

class FileHandler:
	def __init__(self, downloads_location='./downloads', extended=bool) -> None:
			self.downloads_location = downloads_location
			self.extended = extended


	def normalize_name(self, name: str):
		return name.replace('/', '_')


	def track_to_query(self, track: dict):
		track = track['track']
		track_name = track['name'] 
		track_artist = track['artists'][0]['name']
		return f'{track_artist} - {track_name}'
	

	def create_playlist_folder(self, playlist_name: str):
		playlist_name = self.normalize_name(playlist_name)
		if self.extended:
			playlist_folder = f'{self.downloads_location}/Extended Playlists/{playlist_name}'
		else:
			playlist_folder = f'{self.downloads_location}/Playlists/{playlist_name}'
		os.makedirs(playlist_folder, exist_ok=True)
		return playlist_folder


	def write_song(self, filename: str, res: Response):
		filename = self.normalize_name(filename)
		file_location = f'{self.downloads_location}/All Songs/{filename}'

		try:
			with open(file_location, 'wb') as f:
				for chunk in res.iter_content(chunk_size=128):
					f.write(chunk)
		except Exception as e:
			log.exception(e)


	def get_filename(self, track: dict, extended: bool):
		query = self.track_to_query(track)
		file_name = self.normalize_name(query)
		if extended and 'extended' not in query.lower():
			file_name += ' - Extended Mix'
		file_name += '.mp3'
		return file_name

	def delete_old_songs_from_playlist(self, playlist_path: str,
																		track_list: list[str],
																		extended: bool):

		# track_list = [self.get_filename(track, extended) for track in tracks]

		tracks_currently_in_folder = glob.glob(
			f'{playlist_path}/*.mp3')
		for path in tracks_currently_in_folder:
			track = path.split('/')[-1]
			if track not in track_list:
				log.warning(f'Removing {track} from {playlist_path}')
				os.remove(path)


	def copy_track_to_folder(self, playlist_path: str, file_name: str):
		src = f'{self.downloads_location}/All Songs/{file_name}'
		dst = f'{playlist_path}/{file_name}'

		# if track to copy doesnt exist
		if not self.is_file(src): return

		# if track already in folder
		if self.is_file(dst): return

		shutil.copy2(src, dst)


	def load_audiofile(self, file_path: str):
		try:
			audiofile = eyed3.load(file_path)
		except IOError:
			log.error(f"Cannot find {file_path.split('/')[-1]}")
			return

		if audiofile is None:
			log.error(f"Cannot find {file_path.split('/')[-1]}")

		return audiofile


	def get_track_duration(self, file_path: str):
		audiofile = self.load_audiofile(file_path)
		duration = audiofile.info.time_secs
		return duration

	def edit_track_num(self, file_path: str, track_num: tuple[int, int]):
		audiofile = self.load_audiofile(file_path)
		audiofile.tag.track_num = track_num
		audiofile.tag.save()


	def edit_file_metadata(self, file_path:str,
															#  track_num: tuple[int, int] | None,
															 track: dict,
															 song: MP3JuicesSongType,
															 album_cover: Response | None):

		# audiofile = eyed3.load(f'{self.downloads_location}/All Songs/{filename}')
		audiofile = self.load_audiofile(file_path)
		if audiofile is None:
			log.error(f'Cannot find file "{file_path}"')
			return

		if (audiofile.tag == None):
			audiofile.initTag()

		log.debug(f'Editing metadata for {file_path.split("/")[-1]}')
		track = track['track']
		track_name = track['name']
		track_artist = track['artists'][0]['name']
		audiofile.tag.artist = track_artist
		audiofile.tag.title = track_name
		# audiofile.tag.track_num = track_num

		if song.get('album') is not None:
			audiofile.tag.album = song['album']['title']

		if album_cover is not None:
			audiofile.tag.images.set(
				ImageFrame.FRONT_COVER,
				album_cover.content,
				'image/jpeg')

		audiofile.tag.save()

	@staticmethod
	def is_file(file_location: str):
		return os.path.isfile(file_location)
import shutil
import os
import glob

import requests
from requests import Response
import eyed3
from eyed3.core import Tag
from eyed3.id3.frames import ImageFrame
eyed3.log.setLevel("ERROR")

from src import helpers
from src.logger import log
from src.song import MP3JuicesSongType

DOWNLOADS_LOCATION = './downloads'

def set_downloads_location(path: str):
	global DOWNLOADS_LOCATION
	DOWNLOADS_LOCATION = path


def create_playlist_folder( playlist_name: str):
	playlist_name = helpers.normalize_name(playlist_name)
	folder = f'{DOWNLOADS_LOCATION}/{playlist_name}'
	os.makedirs(folder, exist_ok=True)
	return folder


def write_song( filename: str, res: Response):
	filename = helpers.normalize_name(filename)
	file_location = f'{DOWNLOADS_LOCATION}/All Songs/{filename}'

	try:
		with open(file_location, 'wb') as f:
			for chunk in res.iter_content(chunk_size=512):
				f.write(chunk)
	except Exception as e:
		log.exception(e)


def move_track(playlist_name: str, track_filename: str):
	src = f'{DOWNLOADS_LOCATION}/All Songs/{track_filename}'
	dst = f'{DOWNLOADS_LOCATION}/{playlist_name}/{track_filename}'

	if is_file(src) and not is_file(dst):
		shutil.copy2(src, dst)


def load_audiofile( file_path: str):
	try:
		audiofile = eyed3.load(file_path)
	except IOError:
		log.error(f"Cannot find {file_path.split('/')[-1]}")
		return

	if audiofile is None:
		log.error(f"Cannot find {file_path.split('/')[-1]}")
		return

	if (audiofile.tag == None):
		audiofile.initTag()
	return audiofile


def get_track_duration( file_path: str):
	audiofile = load_audiofile(file_path)
	if audiofile is None: return
	duration = audiofile.info.time_secs
	return duration


def edit_track_num( file_path: str, track_num: tuple[int, int]):
	audiofile = load_audiofile(file_path)
	if audiofile is None: return
	audiofile.tag.track_num = track_num
	audiofile.tag.save()


def edit_file_metadata(
		file_path:str,
		track_num: tuple[int, int],
		track: dict,
		# song: MP3JuicesSongType,
		album_cover: Response | None):

	# audiofile = eyed3.load(file_path)
	audiofile = load_audiofile(file_path)

	if audiofile is None:
		log.error(f"Coudn't change Meta Data of {file_path}")
		return

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


def delete_old_songs_from_playlist(playlist_path: str, track_list: list[str]):

	# track_list = [get_filename(track, extended) for track in tracks]

	tracks_currently_in_folder = glob.glob(
		f'{playlist_path}/*.mp3')
	for path in tracks_currently_in_folder:
		track = path.split('/')[-1]
		if track not in track_list:
			log.warning(f'Removing {track} from {playlist_path}')
			os.remove(path)


def is_file(file_location: str):
	return os.path.isfile(file_location)

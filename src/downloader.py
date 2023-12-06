import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future

from src import helpers
from src.logger import log
from src.spotify import Spotipy
# from src.download_client import DownloadClient
from src import download_client as mp3
from src import file_handler as fh

DOWNLOADS_LOCATION = './downloads'

def set_downloads_location(path: str):
	global DOWNLOADS_LOCATION
	DOWNLOADS_LOCATION = path

sp = Spotipy()

def download_playlists():
	with open('./playlists.txt') as f:
		playlist_urls = [
			line.strip()
			for line in f.readlines()
			if line.startswith('https://open.spotify.com/playlist/')
		]

	log.info(f'Found {len(playlist_urls)} playlist.')

	with ProcessPoolExecutor() as executor:
		# executor.map(download_playlist, playlist_urls)
		for url in playlist_urls:
			f = executor.submit(download_playlist, url)
			f.add_done_callback(log_future_exception)
			# download_playlist(url)


def download_playlist(url: str):
	start = time.perf_counter()
	playlist_name = sp.get_playlist_name(url)
	log.info(f'Downloading Playlist: {playlist_name}')

	playlist_name = helpers.normalize_name(playlist_name)
	playlist_path = fh.create_playlist_folder(playlist_name)

	tracks = sp.get_playlist_tracks(url)

	futures = []
	with ThreadPoolExecutor(max_workers=32) as executor:
		for i, track in enumerate(tracks):
			parsed_track = sp.parse_track(track)
			future = executor.submit(download_song, playlist_name, parsed_track, (i+1, len(tracks)))
			future.add_done_callback(log_future_exception)
			futures.append(future)
			# download_song(playlist_name, parsed_track, (i+1, len(tracks)))

	track_list = [future.result() for future in futures if future.result() is not None]
	end = time.perf_counter()
	log.info(f'{playlist_name} time taken: {end-start}')
	fh.delete_old_songs_from_playlist(playlist_path, track_list)


def download_song(playlist_name:str, track: dict, track_num: tuple[int, int]):
	query = f"{track['artists']} - {track['name']}"
	query = helpers.normalize_name(query)
	filename = get_filename(query)

	if alread_downloaded(filename):
		log.debug(f'"{query}" already downloaded.')
		fh.move_track(playlist_name, filename)

		file_path = f'{DOWNLOADS_LOCATION}/{playlist_name}/{filename}'
		fh.edit_track_num(file_path, track_num)
		# if duration == fh.get_track_duration(download_location):
		return filename

	song = mp3.find_song(track, query)
	if song is None: return
	mp3.download_song(filename, song['url'])

	fh.move_track(playlist_name, filename)

	# album_cover = mp3.download_album_cover(song_info)
	album_cover = None
	dst = f'{DOWNLOADS_LOCATION}/{playlist_name}/{filename}'
	fh.edit_file_metadata(dst, track_num, track, album_cover)
	return filename


def alread_downloaded(filename: str):
	path = f'{DOWNLOADS_LOCATION}/All Songs/{filename}'
	if fh.is_file(path):
		return True
	return False


def log_future_exception(future: Future):
	ex = future.exception()
	if ex is not None:
		log.exception(ex)


def get_filename(query: str):
	filename = f'{query}.mp3'
	return filename

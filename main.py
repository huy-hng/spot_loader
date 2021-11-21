# %%
import os

from concurrent.futures import ThreadPoolExecutor

from src.spotify import Spotipy
from src.download_client import MP3Juices
from src.file_handler import FileHandler

playlist_url = 'https://open.spotify.com/playlist/0oWDXsY9BhT9NKimKwNY9d?si=aa622324fb6149f9'

sp = Spotipy()
mp3 = MP3Juices()
fh = FileHandler('Tech House')
tracks = sp.get_playlist_tracks(playlist_url)
track_list = sp.tracks_to_list(tracks)


def download_song(query):
	print(f'\nDownloading {query}')

	versions = mp3.get_song_versions(query)
	if len(versions) == 0:
		print('No versions found. Skipping.')
		return

	version = versions[0]

	name, location = fh.get_name_and_location(version)
	if os.path.isfile(location):
		# skip if file already exists
		print('Song already downloaded.')
		return


	response = mp3.download_song(version)
	if response is None:
		# break 
		return

	fh.write_song(version, response)
	fh.edit_file_metadata(version)

with ThreadPoolExecutor() as executor:
	for query in track_list:
		executor.submit(download_song, query)


# %%
from src.spotify import Spotipy
from src.download_client import MP3Juices
from src.file_handler import FileHandler

playlist_url = 'https://open.spotify.com/playlist/0oWDXsY9BhT9NKimKwNY9d?si=aa622324fb6149f9'

sp = Spotipy()
mp3 = MP3Juices()
fh = FileHandler('Tech House')
tracks = sp.get_playlist_tracks(playlist_url)
track_list = sp.tracks_to_list(tracks)

for query in track_list:
	print(f'Downloading {query}')

	versions = mp3.get_song_versions(query)
	if len(versions) == 0:
		continue

	version = versions[0]
	response = mp3.download_song(version)
	if response is None:
		break
		continue

	fh.write_song(version, response)
	fh.edit_file_metadata(version)
	break

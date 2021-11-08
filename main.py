# %%
import os
import shutil
import json

import requests
from requests import Response
import eyed3

from song import SongType
from spotify import Spotipy

SEARCH_URL = 'https://myfreemp3juices.cc/api/search.php?callback=jQuery213021082371575984715_1635945826190'
def main():
	# songs = get_songs('fly kicks - wax motif remix')
	songs = get_songs('keep raving wax motif')

	download_song(songs[0])

	with open('res.json', 'w') as f:
		f.write(json.dumps(songs))


def get_songs(search_query: str):
	q = search_query.replace(' ', '+')
	payload = {'q': q}

	# retry until proper response or 20 tries
	tries = 20
	parsed = None
	while parsed is None and tries > 0:
		res = requests.post(SEARCH_URL, data=payload)
		parsed = parse_response(res)
		tries -= 1

	if tries == 0:
		raise Exception('No tries left')

	songs: list[SongType] = parsed[1:]
	return songs


def parse_response(res: Response):
	text = res.text
	start_index = text.find('{')
	end_index = text.rfind('}')

	parsed = json.loads(text[start_index:end_index+1])
	return parsed['response']


def download_song(song: SongType):
	artist = song['artist']
	title = song['title']

	filename = f'{artist} - {title}'
	file_location = f'./downloads/{filename}.mp3'

	if os.path.isfile(file_location):
		# check if file already exists, if yes skip
		return

	with requests.get(song['url'], stream=True) as r:
		if r.status_code == 404:
			print(f"Couldn't find {filename}")
			return

		with open(file_location, 'wb') as f:
			shutil.copyfileobj(r.raw, f)


	audiofile = eyed3.load(file_location)
	if audiofile is None:
		return print(f"Coudn't change Meta Data of {filename}")
	audiofile.tag.artist = artist
	audiofile.tag.title = title

	audiofile.tag.save()

def get_spotify_tracks(playlist_url):
	sp = Spotipy()

	tracks = sp.get_playlist_tracks(playlist_url)
	track_list = sp.tracks_to_list(tracks)
	return track_list


if __name__ == '__main__':
	playlist_url = 'https://open.spotify.com/playlist/0oWDXsY9BhT9NKimKwNY9d?si=aa622324fb6149f9'
	song_list = get_spotify_tracks(playlist_url)

	for query in song_list:
		print(f'Downloading {query}')
		songs = get_songs(query)
		if len(songs) == 0:
			print(f'{query} not found.')
			continue
		download_song(songs[0])

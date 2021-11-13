import re

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# from dotenv import load_dotenv
# load_dotenv()


class Spotipy:
	def __init__(self):
		self.sp = spotipy.Spotify(
			client_credentials_manager=SpotifyClientCredentials(
				client_id='55432dffd74d4bb3b7c71e2e2a7a90c2',
				client_secret='5132b52732a84b7db9d9c5e21980d9de'
			)
		)

	def get_playlist_tracks(self, url: str):
		uri = self.get_uri_from_url(url)

		offset = 0
		tracks = []

		items = {'next': True}
		while items['next']:
			items = self.sp.playlist_items(uri, offset=0)
			tracks += items['items']
			offset += 100

		return tracks

	def get_uri_from_url(self, url: str):
		pattern = r'playlist/.+\?'
		result: str = re.findall(pattern, url)[0]
		uri = result[9:-1]
		return uri

	def tracks_to_list(self, tracks):
		track_list = []
		# tracks = tracks['tracks']
		for track in tracks:
			track = track['track']
			search_query = f"{track['name']} {track['artists'][0]['name']}"
			track_list.append(search_query)

		return track_list

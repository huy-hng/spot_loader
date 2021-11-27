import json
from typing import Callable

import requests

from src.logger import log
from src.song import MP3JuicesSongType


class MP3Juices:
	SEARCH_URL = 'https://myfreemp3juices.cc/api/search.php?callback=jQuery213021082371575984715_1635945826190'

	def find_song(self, query: str, duration: int):
		versions = self._get_song_versions(query)
		song = self._choose_version(versions, duration)
		return song

	def _get_song_versions(self, search_query: str):
		""" throws exception if query couldnt be found """
		q = search_query.replace(' ', '+')

		try:
			data = self.retrier(self._search_for_query, search_query=q)
		except Exception as e:
			log.error(f"Couldn't find {search_query} on MP3Juices")

		songs: list[MP3JuicesSongType] = data[1:]
		return songs

	def _search_for_query(self, search_query):
		data = {'q': search_query}
		res = requests.post(self.SEARCH_URL, data=data)

		text = res.text
		start_index = text.find('{')
		end_index = text.rfind('}')

		parsed = json.loads(text[start_index:end_index+1])
		return parsed['response']

	def _choose_version(self, versions: list[MP3JuicesSongType], duration: int):
		""" choose the version that has the duration
				closest to spotify """

		chosen = None
		smallest_diff = 99999
		for version in versions:
			diff = abs(duration - version['duration'])

			if diff < smallest_diff:
				smallest_diff = diff
				chosen = version

		return chosen


	def download_song(self, song: MP3JuicesSongType):
		""" throws exception if song couldnt be downloaded for some reason """
		try:
			return self.retrier(self.request, url=song['url'])
		except Exception as e:
			log.exception(e)
			log.error(f"Couldn't download {song['title']} by {song['artist']}")


	def request(self, url: str):
		res = requests.get(url, stream=True)
		if res.status_code == 404:
			return None
		return res


	def download_album_cover(self, song_info: MP3JuicesSongType):
		title = song_info['title']
		artist = song_info['artist']
		query = f'{title} by {artist}' 

		try:
			album_cover_url = song_info['album']['thumb']['photo_600']
		except Exception as e:
			log.error(f'Album cover not available for {query}')
			return
			
		try:
			return self.retrier(self.request, url=album_cover_url)
		except Exception as e:
			log.exception(e)
			log.error(f'Could not download album cover for {query}')


	@staticmethod
	def retrier(fn: Callable, tries:int=20, **kwargs):
		result = None
		while result is None and tries > 0:
			result = fn(**kwargs)
			tries -= 1

		if tries == 0:
			raise Exception(f'No tries left for {fn.__name__} with args {kwargs}')

		return result
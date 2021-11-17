import json
from typing import Callable

import requests
from requests import Response

from src.song import MP3JuicesSongType


class MP3Juices:
	SEARCH_URL = 'https://myfreemp3juices.cc/api/search.php?callback=jQuery213021082371575984715_1635945826190'

	def get_song_versions(self, search_query: str):
		q = search_query.replace(' ', '+')

		try:
			data = self.retrier(self.get_data, q)
		except Exception as e:
			print(f"Couldn't find {search_query} on MP3JUices")

		songs: list[MP3JuicesSongType] = data[1:]
		return songs


	def get_data(self, search_query):
		data = {'q': search_query}
		res = requests.post(self.SEARCH_URL, data=data)

		text = res.text
		start_index = text.find('{')
		end_index = text.rfind('}')

		parsed = json.loads(text[start_index:end_index+1])
		return parsed['response']


	def download_song(self, song: MP3JuicesSongType):
		try:
			return self.retrier(self.request, song['url'])
		except Exception as e:
			print(e)
			print(f"Couldn't download {song['title']} by {song['artist']}")


	def request(self, url: str):
		res = requests.get(url, stream=True)
		if res.status_code == 404:
			return None
		return res

	

	@staticmethod
	def retrier(fn: Callable, *args, tries:int=20):
		result = None
		while result is None and tries > 0:
			result = fn(args)
			tries -= 1

		if tries == 0:
			raise Exception(f'No tries left for {fn.__name__} with args {args}')

		return result
import json

import requests
from requests import Response

from song import MP3JuicesSongType

SEARCH_URL = 'https://myfreemp3juices.cc/api/search.php?callback=jQuery213021082371575984715_1635945826190'

class MP3Juices:

	def get_songs(self, search_query: str):
		q = search_query.replace(' ', '+')
		payload = {'q': q}

		# retry until proper response or 20 tries
		tries = 20
		parsed = None
		while parsed is None and tries > 0:
			res = requests.post(SEARCH_URL, data=payload)
			parsed = self.parse_response(res)
			tries -= 1

		if tries == 0:
			raise Exception('No tries left')

		songs: list[MP3JuicesSongType] = parsed[1:]
		return songs


	def parse_response(self, res: Response):
		text = res.text
		start_index = text.find('{')
		end_index = text.rfind('}')

		parsed = json.loads(text[start_index:end_index+1])
		return parsed['response']


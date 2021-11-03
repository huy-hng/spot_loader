# %%
import shutil
import json

import requests
from requests import Response
import eyed3

from song import SongType

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
		raise 'No tries left'

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
	filename = f'./download/{artist} - {title}.mp3'

	with requests.get(song['url'], stream=True) as r:
		with open(filename, 'wb') as f:
			shutil.copyfileobj(r.raw, f)

	audiofile = eyed3.load(filename)
	audiofile.tag.artist = artist
	audiofile.tag.title = title

	audiofile.tag.save()


if __name__ == '__main__':
	main()
import os
import time
import difflib
import json
from pprint import pprint

import requests
from requests import Response

import src.file_handler as fh
from src.logger import log
from src.song import MP3JuicesSongType

SEARCH_URL = ''

def parse_url(url: str):
	global SEARCH_URL
	normalized_url = normalize_url(url)
	if normalized_url is None:
		raise Exception('Bad url >:(')
	log.warning(f'Using {normalized_url}...')
	SEARCH_URL = f'https://{normalized_url}/api/search.php?callback=jQuery213021082371575984715_1635945826190'


def get_song(parsed_track: dict, query: str):
	song = find_song(parsed_track, query)
	if song is None: return
	return download_song(song)


def find_song(parsed_track: dict, query: str):
	versions = _get_available_versions(query)

	if not versions:
		log.error(f"Couldn't find {query}")
		return

	# song = _choose_version(versions, duration)
	song = get_highest_score(parsed_track, versions)
	if song is None:
		log.error(f'No versions available for {query}')
	return song


def _get_available_versions(search_query: str):
	""" throws exception if query couldnt be found """
	q = search_query.replace(' ', '+')

	data = None
	try:
		data = _search_for_query(q)
	except Exception as e:
		log.exception(e)
		return
	finally:
		if data is None:
			return

	songs: list[MP3JuicesSongType] = data[1:]

	return songs


def get_highest_score(track, versions):
	sorted_by_score = []
	highest_score = 0
	chosen_version = None

	for version in versions:
		score = version_score(track, version)

		if score > highest_score:
			highest_score = score
			chosen_version = version

		sorted_by_score.append((score, version))

	if chosen_version is None:
		chosen_version = versions[0]

	return chosen_version


def version_score(track, version):
	title_ratio = compare_str(track['name'], version['title'])
	artist_ratio = compare_str(track['artists'], version['artist'])

	extended = 1
	if 'extended' in clean_str(version['title']):
		extended = 0

	remix = 1
	if 'remix' in clean_str(version['title']):
		remix = 0

	dur_diff = duration_ratio(track, version)
	avg = average(title_ratio, artist_ratio, dur_diff[0], remix, extended)
	return avg


def _search_for_query(search_query):
	tries = 20
	parsed = {}
	while parsed.get('response') is None and tries > 0:
		data = {'q': search_query}
		res = request(SEARCH_URL, data=data)

		text = res.text
		start_index = text.find('{')
		end_index = text.rfind('}')

		parsed = json.loads(text[start_index:end_index+1])
		tries -= 1

	return parsed['response']


def _choose_version(versions: list[MP3JuicesSongType], duration: int):
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


def download_song(filename: str, url: str):
	""" throws exception if song couldnt be downloaded for some reason """
	try:
		res = request(url)
		fh.write_song(filename, res)

	except Exception as e:
		# log.exception(e)
		log.error(f"Couldn't download {filename}")
		return


def download_album_cover(song_info: MP3JuicesSongType):
	title = song_info['title']
	artist = song_info['artist']
	query = f'{title} by {artist}'

	try:
		album_cover_url = song_info['album']['thumb']['photo_600']
	except Exception as e:
		log.error(f'Album cover not available for {query}')
		return

	try:
		return request(album_cover_url)
	except Exception as e:
		log.exception(e)
		log.error(f'Could not download album cover for {query}')


def request(url: str, data=None) -> Response:
	tries = 20
	res = None

	while res is None and tries > 0:
		if data is not None:
			res = requests.post(url, data=data)
		else:
			res = requests.get(url, stream=True)
		tries -= 1

	if tries == 0:
		raise Exception(f'No tries left for {url}')

	if res is None or res.status_code == 404:
		raise Exception(f'Bad request')

	return res


def normalize_url(url: str):
	vals = url.split('/')
	vals.reverse()
	for val in vals:
		if val:
			return val
	return


def clean_str(string: str):
	return ''.join(e for e in string if e.isalnum()).lower()


def compare_str(a: str, b: str, junk = None):
	a = clean_str(a)
	b = clean_str(b)
	match = difflib.SequenceMatcher(junk, a, b)
	return match.ratio()


def duration_ratio(track, version):
	ratio = version['duration'] / track['duration']
	# normalized = 1 - abs(1 - ratio)
	clamped = ratio
	if ratio > 1: clamped = 1

	return clamped, ratio


def average(*args):
	return sum(args) / len(args)

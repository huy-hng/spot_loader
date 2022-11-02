import time
import json
import difflib
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, ALL_COMPLETED
from datetime import datetime
from pprint import pprint
from src.song import MP3JuicesSongType
from src.spotify import Spotipy
from src.download_client import DownloadClient


def get_results(futures):
	start = time.perf_counter()
	for track in as_completed(futures):
		track_num, spot_track = futures[track]
		track = track.result()
		print(round(time.perf_counter() - start, 3))

		# print(track_num)
		# if track is None:
		# 	print(spot_track['name'], 'not available')
		# 	print()
		# 	continue
		# print_track(spot_track, track)

	end = time.perf_counter()
	print(f'time taken: {end-start}')


def optimize_query(download_url: str, playlist_url: str):
	# sp = Spotipy()
	mp3 = DownloadClient(download_url)

	# tracks = sp.get_playlist_tracks(playlist_url)
	with open('tests/spotify_tracks_test.json') as f:
		tracks = json.load(f)

	futures = {}
	# with ThreadPoolExecutor() as executor:
	executor = ThreadPoolExecutor(max_workers=32)
		# futures = {executor.submit(get_track, mp3, parse_spotify_track(track)): (i+1, parse_spotify_track(track)) for i, track in enumerate(tracks[135:136])}

	for i, track in enumerate(tracks):
		parsed = parse_spotify_track(track)
		futures[executor.submit(get_track, mp3, parsed)] = (i+1, parsed)

	return futures

	# tracks = wait(futures, return_when=ALL_COMPLETED).done
	# sorted = list(tracks)
	# sorted.sort(key=lambda x: futures[x][0])
	# for track in sorted:
	# 	track_num, spot_track = futures[track]
	# 	# print(track_num)
	# 	track = track.result()
	# 	if track is None:
	# 		print(spot_track['track']['name'], 'not available')
	# 		print()
	# 		continue
	# print_track(spot_track['track'], track)



def get_track(mp3, track):
	query = f'{track["artists"]} {track["name"]}'
	versions = mp3._get_available_versions(query)
	if not versions:
		return None
	return get_highest_score(track, versions)


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

	# sorted_by_score.sort(key=lambda x: x[0], reverse=True)
	# for score, version in sorted_by_score:
	# 	print(round(score, 3))
	# 	pprint(version['url'])
	# 	print(f'title: {version["title"]}')
	# 	print(f'artist: {version["artist"]}')
	# 	print(version['duration'])
	# 	dur_diff = duration_ratio(track, version)
	# 	# dur_diff = round(dur_diff, 3)
	# 	print(f'{dur_diff=}')
	# 	print()

	return chosen_version


def version_score(track, version):
	# fun = lambda x: x == ' '
	# title_match = difflib.SequenceMatcher(fun, track['name'], '')

	complete_query = f'{track["artists"]} {track["name"]}'

	title_ratio = compare_str(track['name'], version['title'])
	artist_ratio = compare_str(track['artists'], version['artist'])

	complete_title_ratio = compare_str(complete_query, version['title'])
	complete_artist_ratio = compare_str(complete_query, version['artist'])

	extended = 1
	if 'extended' in clean_str(version['title']):
		extended = 0

	remix = 1
	if 'remix' in clean_str(version['title']):
		remix = 0


	dur_diff = duration_ratio(track, version)
	avg = average(title_ratio, artist_ratio)
	avg = average(title_ratio, artist_ratio, dur_diff[0], remix, extended)
	return avg


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


#===============================================================================
#                               |=> Helpers <=|
#===============================================================================
def parse_spotify_track(track_info):
	pprint(track_info)
	track = track_info['track']
	return {
		'artists': ' '.join([artist['name'] for artist in track['artists']]),
		'name': track['name'],
		'duration': round(track['duration_ms'] / 1000),
		'album_name': track['album']['name'],
		'album_cover_url': track['album']['images'][0],
	}


def average(*args):
	return sum(args) / len(args)


def print_track(track, version):
	print(f'{track["artists"]} - {track["name"]}')
	print(f'{version["artist"]} - {version["title"]}')

	dur_diff = duration_ratio(track, version)
	dur_diff = round(dur_diff[1], 3)
	print('duration ratio', dur_diff)
	print(version['url'])
	print()

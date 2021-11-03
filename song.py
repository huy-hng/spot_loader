from typing import TypedDict

class SongType(TypedDict):
	artist: str
	title: str
	duration: int
	url: str
	date: int
	album: object

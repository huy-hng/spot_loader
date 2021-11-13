from typing import TypedDict

class MP3JuicesSongType(TypedDict):
	artist: str
	title: str
	duration: int
	url: str
	date: int
	album: object

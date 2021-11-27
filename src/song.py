from typing import TypedDict

class Thumbnail(TypedDict):
	width: int
	height: int
	photo_300: str
	photo_600: str
	photo_1200: str


class Album(TypedDict):
	id: int
	title: str
	owner_id: int
	access_key: str
	thumb: Thumbnail

class MP3JuicesSongType(TypedDict):
	artist: str
	title: str
	duration: int
	url: str
	date: int
	album: Album

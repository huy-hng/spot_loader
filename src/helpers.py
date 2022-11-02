import unidecode

def normalize_name(name: str):
	name = unidecode.unidecode(name)
	return name.replace('/', '_')

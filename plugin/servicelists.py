"""Named snapshots, separate from the active timerplanner.xml."""
import os
from urllib.parse import quote, unquote
from .storage import load_services, save_services


def list_path(directory, name):
	name = name.strip()
	if not name or any(ord(c) < 32 for c in name):
		raise ValueError("Invalid list name")
	filename = quote(name, safe="")
	if len(filename) > 200:
		raise ValueError("List name is too long")
	return os.path.join(directory, filename + ".xml")


def list_names(directory):
	try:
		files = os.listdir(directory)
	except FileNotFoundError:
		return []
	names = []
	for filename in files:
		if filename.endswith(".xml"):
			name = unquote(filename[:-4])
			try:
				path = list_path(directory, name)
			except ValueError:
				continue
			if os.path.basename(path) == filename and os.path.isfile(path):
				names.append(name)
	return sorted(names, key=str.casefold)


def save_list(directory, name, services):
	path = list_path(directory, name)
	os.makedirs(directory, exist_ok=True)
	save_services(path, services)


def load_list(directory, name):
	path = list_path(directory, name)
	if not os.path.isfile(path):
		raise FileNotFoundError(path)
	return load_services(path)


def delete_list(directory, name):
	os.unlink(list_path(directory, name))

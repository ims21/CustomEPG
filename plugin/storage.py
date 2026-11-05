"""Atomic XML storage independent of the Enigma2 UI."""
import json
import os
import tempfile
from xml.etree import ElementTree as ET


def load_services(path):
	try:
		root = ET.parse(path).getroot()
	except FileNotFoundError:
		return []
	except ET.ParseError as error:
		raise ValueError(str(error)) from error
	if root.tag != "customepg" or root.get("version", "1") != "1":
		raise ValueError("Unsupported CustomEPG settings format")
	container = root.find("services")
	if container is None:
		raise ValueError("Missing CustomEPG service list")
	services = []
	seen = set()
	for node in container:
		ref = node.get("reference")
		if node.tag != "service" or not ref:
			raise ValueError("Invalid CustomEPG service entry")
		if ref not in seen:
			services.append((ref, node.get("name", "")))
			seen.add(ref)
	return services


def load_legacy_services(path):
	"""Read the first prototype's JSON only when no XML exists. Never rewrite it."""
	try:
		with open(path, "r", encoding="utf-8") as source:
			data = json.load(source)
	except FileNotFoundError:
		return []
	if not isinstance(data, dict) or data.get("version") != 1:
		raise ValueError("Unsupported CustomEPG settings format")
	services = data.get("services")
	if not isinstance(services, list) or any(not isinstance(ref, str) or not ref for ref in services):
		raise ValueError("Invalid CustomEPG service list")
	return [(ref, "") for ref in dict.fromkeys(services)]


def save_services(path, services):
	root = ET.Element("customepg", version="1")
	root.text = "\n\t"
	container = ET.SubElement(root, "services")
	container.text = "\n\t\t" if services else None
	container.tail = "\n"
	for ref, name in services:
		node = ET.SubElement(container, "service", reference=ref, name=name)
		node.tail = "\n\t\t"
	if len(container):
		container[-1].tail = "\n\t"
	# Replace only after a complete write; unsuccessful saves preserve the old file.
	fd, temporary = tempfile.mkstemp(prefix=".customepg-", dir=os.path.dirname(path))
	try:
		with os.fdopen(fd, "wb") as target:
			os.fchmod(target.fileno(), 0o644)
			ET.ElementTree(root).write(target, encoding="utf-8", xml_declaration=True)
			target.write(b"\n")
			target.flush()
			os.fsync(target.fileno())
		os.replace(temporary, path)
	finally:
		if os.path.exists(temporary):
			os.unlink(temporary)

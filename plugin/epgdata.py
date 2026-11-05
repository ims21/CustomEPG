"""EPG row handling. Row format is OpenPLi's RIBDT."""


def event_key(row):
	# Event IDs are only unique within a service, and may later be reused.
	return (row[0], row[1], row[2]) if row else None


def collect_events(query, references, begin):
	references = list(dict.fromkeys(references))
	if not references:
		return []
	# -1 means no end-time limit, as in OpenPLi EPGList.fillSingleEPG.
	rows = query(['RIBDT'] + [(ref, 0, begin, -1) for ref in references]) or []
	result = []
	seen = set()
	for row in rows:
		if len(row) != 5 or not row[0] or row[1] is None or row[2] is None or row[3] is None:
			continue
		key = event_key(row)
		if key not in seen:
			seen.add(key)
			result.append(tuple(row[:4]) + (row[4] or "",))
	return result


def sort_events(rows, sorting, rating=None):
	if sorting == 2:
		return sorted(rows, key=lambda row: (rating(row), row[2], row[0], row[1]))
	if sorting == 1:
		return sorted(rows, key=lambda row: (row[4].lower(), row[2], row[0], row[1]))
	return sorted(rows, key=lambda row: (row[2], row[4].lower(), row[0], row[1]))


def selection_index(rows, selected=None, now=None):
	if selected is not None:
		for index, row in enumerate(rows):
			if event_key(row) == selected:
				return index
	if now is not None:
		for index, row in enumerate(rows):
			if row[2] + row[3] > now:
				return index
	return 0

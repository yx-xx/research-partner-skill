"""Check DOIs against Crossref and print what each one is, so that it can be compared with what the paper cites.

  python check_dois.py 10.1016/j.rse.2017.06.031 10.5281/zenodo.1234567
  python check_dois.py --bib refs.bib          every doi = {...} of a BibTeX file

Exit status 1 if a DOI does not resolve. It only asks Crossref (api.crossref.org) for the public metadata of the DOI,
nothing else leaves the computer. A DOI that Crossref does not know (e.g. one of DataCite, like Zenodo's) is looked up
at DataCite. Then READ the title, authors and year: a DOI that resolves to another paper is as wrong as one that does
not resolve.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

AGENT = 'scientific-paper-skill (doi check)'


def _get(url):
	request = urllib.request.Request(url, headers={'User-Agent': AGENT, 'Accept': 'application/json'})
	with urllib.request.urlopen(request, timeout=30) as response:
		return json.load(response)


def crossref(doi):
	m = _get('https://api.crossref.org/works/' + urllib.parse.quote(doi))['message']
	year = (m.get('issued', {}).get('date-parts') or [[None]])[0][0]
	names = ['%s %s' % (a.get('family', a.get('name', '?')), (a.get('given') or '')[:1]) for a in m.get('author', [])]
	return {'source': 'Crossref', 'title': (m.get('title') or ['?'])[0], 'authors': names, 'year': year,
	        'venue': (m.get('container-title') or [''])[0], 'type': m.get('type'),
	        'retracted': any(u.get('type') == 'retraction' for u in m.get('update-to', []) or [])}


def datacite(doi):
	m = _get('https://api.datacite.org/dois/' + urllib.parse.quote(doi))['data']['attributes']
	names = [c.get('name', '?') for c in m.get('creators', [])]
	return {'source': 'DataCite', 'title': (m.get('titles') or [{}])[0].get('title', '?'), 'authors': names,
	        'year': m.get('publicationYear'), 'venue': m.get('publisher') or '',
	        'type': (m.get('types') or {}).get('resourceTypeGeneral'), 'retracted': False}


def check(doi):
	doi = re.sub(r'^(https?://(dx\.)?doi\.org/|doi:)', '', doi.strip(), flags=re.I)
	for lookup in (crossref, datacite):
		try:
			return doi, lookup(doi)
		except (urllib.error.HTTPError, KeyError):
			continue
		except urllib.error.URLError as error:
			return doi, {'error': 'no network: %s' % error.reason}
	return doi, None


def bib_dois(path):
	with open(path, encoding='utf-8') as f:
		return re.findall(r'doi\s*=\s*[{"]\s*([^}"\s]+)', f.read(), flags=re.I)


def main():
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('dois', nargs='*')
	parser.add_argument('--bib', help='a BibTeX file: every doi field in it')
	args = parser.parse_args()
	dois = args.dois + (bib_dois(args.bib) if args.bib else [])
	if not dois:
		parser.error('give DOIs or --bib')
	bad = 0
	for d in dois:
		doi, info = check(d)
		if not info or 'error' in info:
			bad += 1
			print('FAIL  %s  %s' % (doi, info['error'] if info else 'does not resolve (Crossref, DataCite)'))
			continue
		authors = ', '.join(info['authors'][:3]) + (' et al.' if len(info['authors']) > 3 else '')
		flag = '  *** RETRACTED ***' if info['retracted'] else ''
		print('OK    %s  [%s]%s\n        %s (%s)\n        %s\n        %s' % (
			doi, info['source'], flag, authors, info['year'], info['title'], info['venue']))
	print('\n%d checked, %d failed. Compare each title, author and year with the citation in the paper.' % (
		len(dois), bad))
	return 1 if bad else 0


if __name__ == '__main__':
	sys.exit(main())

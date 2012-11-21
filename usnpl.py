import scrapelib, csv, BeautifulSoup, re, sys
from soupselect import select

def getdomain(s):
	re_domain = re.compile(r'http://(www\.)?(.*?)/', re.I)
	m = re_domain.search(s)
	if m is not None:
		return m.group(2)
	else:
		return ''

def main():
	s = scrapelib.Scraper(requests_per_minute=10)

	targets = {
		re.compile(r'/(?P<state>\w{2})tv_mob\.php'): [
			'tv',
			None, 
			re.compile(r'<b>(.*?)<\/b>\s*\n\s*&nbsp;?\s*\n\s*<a href="(.*?)">(.*?)<\/a>\s*\n\s*\s*\n\s*\(<a href=\'(.*?)\'>A<\/a>\)\s*\n\s*<br>', re.I|re.M|re.S)
		],

		re.compile(r'/(?P<state>\w{2})radio_mob\.php'): [
			'radio',
			None, 
			re.compile(r'<b>(.*?)<\/b>\s*\n\s*\s*\n\s*<a href="(.*?)">(.*?)<\/a>\s*\n\s*\s*\n\s*(.*?)&nbsp;?\s*\n\s*(.*?)\s*\n\s*<br>', re.I|re.M|re.S)
		],

		re.compile(r'/(?P<state>\w{2})news_mob\.php'): [
			'news',
			None, 
			re.compile(r'<b>(.*?)<\/b>\s*\n\s*&nbsp;?<a href="(.*?)">(.*?)<\/a>\s*\n\s*\(<a href="(.*?)">A<\/a>\)', re.I|re.S)
		],
	}

	# only create writer objects for datatypes we're collecting
	# we don't want to overwrite existing files, after all
	for (t, (entry_type, entry_writer, entry_extractor)) in targets.items():
		if (('--%s' % entry_type) in sys.argv) or ('--all' in sys.argv):
			targets[t][1] = csv.writer(open('usnpl_%s.csv' % entry_type, 'w'))

	state_count = {}
	for x in map(lambda x: x[0], targets.values()):
		state_count[x] = {}

	soup = BeautifulSoup.BeautifulSoup(s.urlopen('http://mobile.usnpl.com/'))
	links = select(soup, 'td a')

	for link in links:
		for (t, (entry_type, entry_writer, entry_extractor)) in targets.items():		 

			# figure out if this is a news/radio/tv link		
			state_link_m = t.search(str(link))
			if state_link_m is not None and entry_writer is not None:			

				state = state_link_m.group('state') # define the state
				try:
					state_html = s.urlopen(link.get('href')) # grab the corresponding page			
				except:
					continue

				# find all matching entries			
				for m in re.finditer(entry_extractor, str(state_html)):				
					entry_writer.writerow((state,) + m.groups())

					if not state_count[entry_type].has_key(state):
						state_count[entry_type][state] = 0
					state_count[entry_type][state] += 1

				print '%s/%s: %3d - %s' % (entry_type, state, state_count[entry_type][state], link.get('href'))



if __name__ == '__main__':
	if len(sys.argv)==1:
		print """
=====USNPL Scraper=====

Usage: any one of the following 

	python usnpl.py --tv
	python usnpl.py --radio
	python usnpl.py --news

will generate a CSV file extracted from usnpl.com for the appropriate media type. Alternately,
	
	python usnpl.py --all 

will generate all three CSVs on a single run.
"""
	
	else:
		main()


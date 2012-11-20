import scrapelib, csv, BeautifulSoup, re, sys
from soupselect import select

def getdomain(s):
	re_domain = re.compile(r'http://(www\.)?(.*?)/', re.I)
	m = re_domain.search(s)
	if m is not None:
		return m.group(2)
	else:
		return ''

writer = csv.writer(sys.stdout)

s = scrapelib.Scraper(requests_per_minute=10)

soup = BeautifulSoup.BeautifulSoup(s.urlopen('http://usnpl.com'))

states = select(soup, '#data_box a')

re_usnpl = re.compile(r'uspnl\.com', re.I)
re_paper_link = re.compile(r'^&nbsp;?<a href="(.*?)">(.*?)</a>', re.I|re.M|re.S)

for state_link in states:
	state_soup = BeautifulSoup.BeautifulSoup(s.urlopen(state_link.get('href')))
	data_boxes = select(state_soup, "div")	
	for div in data_boxes:
		if div.get('id')=='data_box':
			if "<h3>Newspapers</h3>" in str(div):				
				for m in re.finditer(re_paper_link, str(div)):
					writer.writerow((m.group(2).strip(), m.group(1).strip(), getdomain(m.group(1)).strip()))
					

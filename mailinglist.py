#######################################################
#Program: mailinglist.py
#Author: Tyler Fornes
#Date: 2/26/15
#Purpose: Scrapes email addresses starting at specified
#root domain. Page depth set to three by default
#######################################################
from bs4 import BeautifulSoup
import requests,sys,urlparse,re


#Get root URL from command line input
rootURL = sys.argv[1]
#Sets recursion level for crawler
setLevel = 3

#Determines the base domain from the root URL
base_domain = urlparse.urlparse(rootURL).hostname

#Global lists
emails = []
allURLS = []
#Appends the input URL into the list (level 1)
allURLS.append(rootURL)

#Function to perform URL lookups from scraped URLS
#parameters: tempURL-URL to scrape
#			 pageLevel- depth of crawl
def recursiveURLLookup(tempURL, pageLevel, parentURLS):

	#URLs at or above current page level
	masterURLS = []
	#URLs found at current temp URL
	slaveURLS = []

	try:
		#Gets HTML data from page
		reqData  = requests.get(tempURL)
		contentType = reqData.headers['content-type']
		#if content type is html, proceed to get page, else return error message
		if('text/html' in contentType):
			print "Scraping URLs at Depth %s: %s" % (pageLevel + 1, tempURL)
			HTMLdata = unicode(reqData.text)
			soup = BeautifulSoup(HTMLdata)

			#Finds all href tags
			for link in soup.find_all('a'):
				temp_url = link.get('href')
				#Error checking for empty tag
				if temp_url is not None:
					#Determining whether the link is absolute or relative
					if not(bool(urlparse.urlparse(temp_url).netloc)):
						temp_url = urlparse.urljoin(sys.argv[1],temp_url)
					#Compares URL against root domain, only keeps links within domain
					temp_base_domain = urlparse.urlparse(temp_url).hostname
					if(temp_base_domain == base_domain):
						slaveURLS.append(temp_url)

			#Push unique URLs into master list
			slaveURLS = sorted(set(slaveURLS))
			masterURLS = slaveURLS

			#Cycle through slave URLs and perform recursive URL lookup, given still in depth
			if(pageLevel < setLevel - 1):
				for url in slaveURLS:
					returnedArray = recursiveURLLookup(url, pageLevel + 1, masterURLS)
					masterURLS.extend(list(set(parentURLS) - set(returnedArray)))
                                print "%s - Level %s" % (masterURLS, pageLevel)
		else:
			print "ContentType Mismatch [%s]: %s" % (contentType, tempURL)
	except:
		print "Error: Probably misformatted URL"

	#Return master list
	return masterURLS

#Performs initial lookup, to start recursive function
allURLS.extend(recursiveURLLookup(rootURL, 1, []))
#Ensures all items in list are unique
allURLS = sorted(set(allURLS))

print "\n\n"
print "Scraping for addresses"

#Scrape each unique page for email addresses
for index in range(len(allURLS)):
	req  = requests.get(allURLS[index])
	#Get page content type
	contentType = req.headers['content-type']
	#if html page, get email addresses
	if('text/html' in contentType):
		html = req.text
		email_sleuth = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}",html)
		emails.extend(email_sleuth)

print "\n\n"

#Sort for unique email addresses
emails = sorted(set(emails))
#Write all unique addresses found from scrape to file
out = open("scraped_addresses.txt", "w")
for index in range(len(emails)):
	out.write(emails[index] + '\n')
out.close()


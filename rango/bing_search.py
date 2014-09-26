import json
import urllib, urllib2

def main():
	search_terms = raw_input('Enter search terms: ')
	results_list = run_query(search_terms)

	rank = 1
	for results in results_list:
		print "{0}. {1}, {2}".format(rank, results['title'], results['link'])
		rank += 1

def run_query(search_terms):
	root_url = 'https://api.datamarket.azure.com/Bing/Search/'
	source = 'Web'

	# specify no. of results to return and from where
	results_per_page = 10
	offset = 0

	# wrap query in quotes for the API
	query = "'{0}'".format(search_terms)
	query = urllib.quote(query)

	# complete the search query url
	search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
		root_url,
		source,
		results_per_page,
		offset,
		query)

	# auth bing servers
	username = ''
	bing_api_key = 'SWxayFibuuxbONCjAvhVamu3DKZmYjUN9c5gw/1zXYI'

	# password manager to handle auth
	password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
	password_mgr.add_password(None, search_url, username, bing_api_key)

	# populate results
	results = []

	try:
		handler = urllib2.HTTPBasicAuthHandler(password_mgr)
		opener = urllib2.build_opener(handler)
		urllib2.install_opener(opener)

		# connect to server and read response
		response = urllib2.urlopen(search_url).read()

		# convert to Python dictionary
		json_response = json.loads(response)

		# loop through pages returned
		for result in json_response['d']['results']:
			results.append({
				'title': result['Title'],
				'link': result['Url'],
				'summary': result['Description']
				})

		# catch a URLError - connection issue
	except urllib2.URLError, e:
		print "Error when querying the Bing API: ", e

	return results
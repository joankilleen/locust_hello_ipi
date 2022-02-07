"""Tempoary testing file - TODO Delete"""
import requests
import json
import urllib
HEADER_IPI_VERSION = 'X-IPI-VERSION'
_x_ipi_version = None
host = 'https://dev-database.ipi.ch'

# Get X-IPI-Version
response = requests.get(host + '/database/')
_x_ipi_version = response.headers['X-IPI-VERSION']
print('X-IPI-VERSION: ', _x_ipi_version)


# Query with filter
headers = {
    HEADER_IPI_VERSION: _x_ipi_version,
    'Accept': 'application/json'}
search_url = host + '/database/resources/query/chmarke/search?" + \
    "ps=5&f=schutztiteltyp__type_i18n%23global.bo.enum.schutztiteltyp.ch.marke&" + \
    "f=hinterlegungsdatum__type_date%23LAST_YEAR&sf=score&so=DESC'
dyn_search_url = host + '/database/resources/query/chmarke/search?'

filters = ''.join(
    'schutztiteltyp__type_i18n#global.bo.enum.schutztiteltyp.ch.marke, eintragungsdatum__type_date#LAST_YEAR').split()

for f in filters:
    dyn_search_url += urllib.parse.urlencode({'f': f})

dyn_search_url += '&' + urllib.parse.urlencode({'ps': '5', 'sf': 'score', 'so': 'DESC'})
print('final search_url', dyn_search_url)
print('origi search_url', search_url)
# Extract query data from metadata
with requests.get(url=search_url, headers=headers) as response_query:
    metadata = None
    if response_query.status_code == 200:
        metadata = response_query.json()['metadataAsTransit']
        print('Type of metadata', type(metadata))
        querydata = json.loads(metadata)['~#resultmeta']['~:query']
        print('Type of querydata', type(querydata))
        print('Search sucessful. Length metadata:', len(metadata), search_url)
    else:
        print('Query not successful status code:', 'url: ', search_url, response_query.status_code)
        exit()

# Export as PDF
# https://i-database.ipi.ch/database/resources/export/itemslist/pdf;lang=de
export_url = host + '/database/resources/export/itemslist/pdf;lang=de'
headers['Content-Type'] = 'application/transit+json'
headers['Accept'] = '*/*'
headers['X-IPI-VERSION'] = _x_ipi_version

print('\nSending export request with query data:\n', 'headers:',
      headers, 'url:', export_url)
with requests.post(url=export_url, headers=headers, json=querydata) as response_export:
    if response_export.status_code != 200:
        print('Export not successful', response_export.status_code)
    else:
        print('Export successful!')
        print(len(response_export.content))

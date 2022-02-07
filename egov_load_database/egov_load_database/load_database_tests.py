''' EGov Database API Load Tests. Define parameters in locust.conf'''


import requests
import logging
import helper._argument_handler as argument_handler
import json
from locust import task, HttpUser, events

HEADER_IPI_VERSION = 'X-IPI-VERSION'
HEADER_ACCEPT = 'Accept'
HEADER_CONTENT_TYPE = 'Content-Type'

URL_DATABASE = '/database'
URL_RESOURCES = URL_DATABASE + '/resources'
URL_QUERY = URL_RESOURCES + '/query'
URL_EXPORT = URL_RESOURCES + '/export/itemslist'
URL_FETCH = URL_QUERY + '/fetch'

QUERY_TYPE = {'hoheitszeichen': 'hoheitszeichen', 'marken': 'chmarke'}

EGOV_ARG_SEARCH_FILTERS = 'egov_search_filters'
EGOV_ARG_DATABASE = 'egov_database'
EGOV_ARG_PAGE_SIZE = 'egov_page_size'
EGOV_ARG_EXPORT_TYPE = 'egov_export_type'

_custom_arguments = None
_x_ipi_version = None


def log_to_locust(logging_level, text):
    '''Handle logging to locust. Log file name defined in locust.conf
    return: None'''
    logger = logging.getLogger('locust')
    logger.log(logging_level, text)


@events.init.add_listener
def _read_x__ipi_version(environment, **kwargs):
    # pylint: disable=unused-argument
    '''Reading the X_IPI_VERSION header which must be used in all requests to Database API.
    Sets global: _x_ipi_version'''

    global _x_ipi_version
    response = requests.get(environment.host + URL_DATABASE)
    _x_ipi_version = response.headers['X-IPI-VERSION']
    log_to_locust(logging.INFO, f'IPI header version extracted: {_x_ipi_version}')


@events.init_command_line_parser.add_listener
def _add_custom_arguments(parser):
    '''Reading the arguments for the egov database search. See locust.conf file.
    return: None'''

    global _custom_arguments
    _custom_arguments = argument_handler.read_egov_arguments(parser)
    # have to print because logging not up and running yet
    print('EGov custom arguments read from locust.conf:')
    for k, v in _custom_arguments.items():
        print(f'{k} : {v}')


class DatabaseAPI(HttpUser):
    ''' Database API locust tasks'''

    def start_query(self):
        '''Start query using parameters in locust.conf
        return: metadata and querydata extracted from response'''
        headers = {
            HEADER_IPI_VERSION: _x_ipi_version,
            HEADER_ACCEPT: 'application/json'}

        metadata = None
        querydata = None
        query_type = QUERY_TYPE[_custom_arguments[EGOV_ARG_DATABASE]]
        search_url = f'{self.host}{URL_QUERY}/{query_type}/search?{_custom_arguments[EGOV_ARG_SEARCH_FILTERS]}'

        with self.client.get(url=search_url, headers=headers, name='T00-Database query') as response_query:
            if response_query.status_code == 200:
                metadata = response_query.json().get('metadataAsTransit')
                querydata = json.loads(metadata)['~#resultmeta']['~:query']
            else:
                log_to_locust(logging.WARN, f'Query not successful: {response_query.status_code} received')
        return (metadata, querydata)

    @task
    def query_export(self):
        '''Locust task: Perform a database query and export the results.
        Only possible for Ch Marke und geschuetzte Zeichen
        return: None'''

        # Validate the query
        egov_search_filters = _custom_arguments[EGOV_ARG_SEARCH_FILTERS]
        if not 'ch.marke' in egov_search_filters and not 'geschuetzteszeichen' in egov_search_filters:
            log_to_locust(
                logging.WARN,
                f'Export not possible because of egov_search_filter types {egov_search_filters}')
            return

        # pylint: disable=unused-variable
        metadata, querydata = self.start_query()

        export_type = _custom_arguments[EGOV_ARG_EXPORT_TYPE]
        export_url = f'{self.host}{URL_EXPORT}/{export_type}'
        headers = {
            HEADER_CONTENT_TYPE: 'application/transit+json',
            HEADER_ACCEPT: '*/*',
            HEADER_IPI_VERSION: _x_ipi_version}

        with self.client.post(url=export_url, headers=headers, json=querydata, name='T01-Export query results') \
                as response_export:
            if response_export.status_code != 200:
                log_to_locust(logging.WARN, 'Export not successful: ')
                response_export.failure('Export not successful: ')
            else:
                log_to_locust(logging.DEBUG, 'Export successful!')

    @task
    def query_fetch_next_page(self):
        '''Locust task: Perform a query and fetch the next page
        return: None'''

        # pylint: disable=unused-variable
        metadata, querydata = self.start_query()
        page_size = _custom_arguments[EGOV_ARG_PAGE_SIZE]
        fetch_url = f'{URL_FETCH}?ps={page_size}'
        headers = {
            HEADER_CONTENT_TYPE: 'application/transit+json',
            HEADER_ACCEPT: '*/*',
            HEADER_IPI_VERSION: _x_ipi_version}

        with self.client.post(url=fetch_url, headers=headers, data=metadata, name='T02-Fetch one page') \
                as response_fetch:
            if response_fetch.status_code != 200:
                log_to_locust(logging.WARN, 'Fetch not successful: ')

"""Handles custom arguments for the database api. All egov parameters set in locust.conf"""

import urllib

EGOV_DATABASE_ALLOWED_VALUES = ["hoheitszeichen", "marken"]
EGOV_EXPORT_ALLOWED_VALUES = ["pdf", "csv"]


def read_egov_arguments(parser):
    parser.add_argument("--egov_database", type=str, env_var="LOCUST_EGOV_DATABASE",
                        help=f"Which egov database? {EGOV_DATABASE_ALLOWED_VALUES}")
    egov_database = parser.parse_known_args()[0].egov_database

    if not egov_database in EGOV_DATABASE_ALLOWED_VALUES:
        print(
            f"The value of egov_database {egov_database} is not allowed."
            + f"Use values: {EGOV_DATABASE_ALLOWED_VALUES}. See locust conf file.")
        exit()

    # page size
    parser.add_argument("--egov_page_size", type=int, env_var="LOCUST_EGOV_PAGE_SIZE",
                        help="size of page fetch")

    egov_page_size = parser.parse_known_args()[0].egov_page_size

    parser.add_argument("--egov_search_filters", type=str, env_var="LOCUST_EGOV_SEARCH_FILTERS",
                        help="egov search filters (do not includef= or \"\")")

    egov_search_filters = parser.parse_known_args()[0].egov_search_filters

    filters = egov_search_filters.replace(" ", "").split(",")

    parser.add_argument("--egov_export_type", type=str, env_var="LOCUST_EGOV_EXPORT_TYPE",
                        help=f"Which export type? {EGOV_EXPORT_ALLOWED_VALUES}")
    egov_export_type = parser.parse_known_args()[0].egov_export_type

    # Validation
    if len(filters) == 0:
        print("No egov_search_filters defined for the query. See locust.conf")
        exit()
    if not egov_page_size > 0:
        print("No egov_page_size defined for the query. See locust.conf")
        exit()
    if not egov_export_type in EGOV_EXPORT_ALLOWED_VALUES:
        print(f"Export txpe not recognised. Ue one of {EGOV_EXPORT_ALLOWED_VALUES}")

     # Url encode the search filters
    if "%" in filters[0]:
        search_params = "f=" + filters[0]
    else:
        search_params = urllib.parse.urlencode({"f": filters[0]})

    for f in range(1, len(filters)):
        if "%" in filters[0]:
            search_params = "&f=" + filters[0]
        else:
            search_params += "&" + urllib.parse.urlencode({"f": filters[f]})

    # Add in the standard filters 'ps=5&sf=score&so=DESC'
    search_params += "&" + urllib.parse.urlencode({"ps": egov_page_size, "sf": "score", "so": "DESC"})

    # Store all custom arguments
    custom_arguments = {
        "egov_database": egov_database,
        "egov_search_filters": search_params,
        "egov_page_size": egov_page_size,
        "egov_export_type": egov_export_type
    }
    return custom_arguments

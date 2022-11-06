import requests
from bs4 import BeautifulSoup
import json  # used by get_herold_telefonbuch_matches()

from dotenv import load_dotenv  # .env is storing Google developer key
import os
from googleapiclient.discovery import build  # used by get_google_at_matches()
from googleapiclient.errors import HttpError

import logging

load_dotenv()
GOOGLE_DEVELOPER_KEY = os.environ.get('GOOGLE_DEVELOPER_KEY')

def get_telefonabc_matches(lastname) -> int:
    """ takes 'lastname' and returns number of matches for telefonabc.at as integer """
    # strange shortened latin1 umlaut encoding
    lastname = lastname.replace("ö", "%F6")
    lastname = lastname.replace("ä", "%E4")
    lastname = lastname.replace("ü", "%FC")
    lastname = lastname.replace("ß", "%DF")

    url = "https://www.telefonabc.at/result.aspx?what=" + lastname + "&where=&exact=False&firstname=&lastname=&appendix=&branch=&p=0&sid=&did=&cc="
    page = requests.get(url)

    if page.status_code == 404:
        soup = BeautifulSoup(page.content, 'html.parser')
        html_snippet = soup.find('div', class_="info").get_text()
        if html_snippet.find("Keine Treffer") > 1:  # if snippet does not contain 'keine Treffer', -1 is returned
            return 0
        else:
            quit("ERROR: unexpected response format")

    elif page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        html_snippet = soup.find('div', class_="info").get_text()
        matches = [int(s) for s in html_snippet.split() if s.isdigit()][0]
        return matches


def get_google_at_matches(lastname) -> int:
    """ takes 'lastname' and returns number of matches for google.at as integer """
    # search engine (CX parameter): see https://programmablesearchengine.google.com/controlpanel/all
    # API key: see https://console.cloud.google.com/apis/credentials

    service = build(
        "customsearch", "v1", developerKey=GOOGLE_DEVELOPER_KEY
    )

    try:
        res = (
            service.cse()
            .list(
                q=lastname,  # query
                cx="832f9209602714d00",  # custom search engine ID
                cr="countryAT"  # country restriction
            )
            .execute()
        )

        # return res    # full search results as dict
        return int(res['searchInformation']['totalResults'])

    except HttpError as e:
        logging.error('Error response status code %d, reason %s:', e.resp.status, e.content)
        return None



def get_herold_telefonbuch_matches(lastname) -> int:
    """ takes 'lastname' and returns number of matches for herold.at/telefonbuch as integer """
    url = "https://www.herold.at/telefonbuch/suche/?userTerm=" + lastname
    page = requests.get(url, timeout=15)

    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'html.parser')
        html_snippet = soup.find(id="__NEXT_DATA__").get_text()
        j = json.loads(html_snippet)
        return int(j['props']['pageProps']['results']['totalCount'])


# Example

# lastname = "Doppelbaur"
# print(f"\nSuche nach '{lastname}'")
# print("Telefonbuch.abc:", get_telefonbuchabc_matches(lastname))
# print("Google.com:", get_google_at_matches(lastname))
# print("Herold.at:", get_herold_telefonbuch_matches(lastname))

# will return:
"""
Suche nach 'Doppelbauer'
Telefonbuch.abc: 85
Google.com: 43900
Herold.at: 96

Suche nach 'Doppelbaur'
Telefonbuch.abc: 0
Google.com: 6
Herold.at: 0

Suche nach 'Oberberger'
Telefonbuch.abc: 9
Google.com: 5530
Herold.at: 13
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Aug 10, 2017
.. codeauthor: svitlana vakulenko
<svitlana.vakulenko@gmail.com>

Look up the keyword in Google Custom Search API to get search snippets
'''
import requests

from settings import *

# e.g. GET https://www.googleapis.com/customsearch/v1?key=INSERT_YOUR_API_KEY&cx=017576662512468239146:omuauf_lfve&q=lectures
GOOGLE_SEARCH_API = 'https://www.googleapis.com/customsearch/v1?key=' + GOOGLE_API_KEY + '&cx=' + GOOGLE_CUSTOM_SE + '&q='


def search_google(query):
    doc = []
    resp = requests.get(GOOGLE_SEARCH_API+query)
    results = resp.json()
    if 'items' in results.keys():
        for result in results['items']:
            title = result['title']
            print (title)
            doc.append(title)
            snippet = " ".join(result['snippet'].split(' ... ')[1:]).strip('\n')
            print snippet
            doc.append(snippet)
            print result['link']
            print '\n'
    return " ".join(doc)


def test_search_google():
    search_google(SEED)


if __name__ == '__main__':
    test_search_google()

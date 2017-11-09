# -*- coding: utf-8 -*-
'''
svakulenko
9 Nov 2017
'''
from elasticsearch import Elasticsearch

es = Elasticsearch()

# reset index
try:
    es.indices.delete(index=index_name)
    es.indices.create(index=index_name, body=mapping)
except Exception as e:
    print (e)

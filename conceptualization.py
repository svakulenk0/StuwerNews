# -*- coding: utf-8 -*-
'''
svakulenko
17 july 2017
'''
import requests
import json
import rdflib

from settings import BABELFY_KEY

SEED = 'stuwerviertel'

LOTUS_API = "http://lotus.lodlaundromat.org/retrieve?match=%s&predicate=label&minmatch=100&cutoff=0.005&rank=%s&size=%i&string=%s"
LODALOT_API = 'http://webscale.cc:3001/LOD-a-lot?%s=%s'

BABELFY_API = 'https://babelfy.io/v1/disambiguate'


def babelfy_query(text, lang='EN', match='EXACT_MATCHING', candidates='TOP'):
    params = {
        'text': text,
        'lang': lang,
        'match': match,
        'cands': candidates,
        'posTag': 'NOMINALIZE_ADJECTIVES',
        'key': BABELFY_KEY,
        'dens': 'true'
    }
    resp = requests.post(BABELFY_API, data=params)
    return [hit['DBpediaURL'] for hit in resp.json()]


def lotus_recursive_call(original, found_texts=[], found_concepts=[], size=10, filter_ns=False, verbose=False):
    '''
    '''
    # avoid calling the API several times for the same term
    if original not in found_texts:
        concepts, found_text = get_concepts_from_lotus(original, size=size, filter_ns=filter_ns)
        
        if found_text:
            if verbose:
                print (found_text)
                print (concepts)
                print ('\n')
            found_texts.append(found_text)
            found_concepts.append(concepts)
            # process the rest of the string
            leftover = original.replace(found_text, "").strip()
        else:
            # skip the 1st word
            leftover = " ".join(original.split(" ")[1:])
        if leftover:
            lotus_recursive_call(leftover, found_texts, found_concepts, filter_ns=filter_ns, verbose=verbose)
        
        if found_concepts:
            return found_concepts
        else:
            return None


def loop_concept_expansion(concept_uris, visited=[], nhops=2, descriptions=[]):
    if len(visited) < nhops:
        for concept in concept_uris:
            if concept not in visited:
                nns, description = lookup_nns(concept)
                if description:
                    descriptions.append(description)
                visited.append(concept)
                if nns:
                    # print concept
                    # print nns
                    # print '\n'
                    # recursion
                    loop_concept_expansion(nns, visited)
    return (visited, descriptions)


def get_concepts_from_lotus(text, match='phrase', rank='lengthnorm', size=5, filter_ns=False):
# def get_concepts_from_lotus(text, match='terms', rank='lengthnorm', size=5, filter_ns='dbpedia'):
    '''
    recursive call to the API
    returns a list of concept URIs from LOTUS API
    sample request to LOTUS API: http://lotus.lodlaundromat.org/retrieve?string=monkey
    Params:
    langtag=en&match=conjunct&rank=psf&size=5&
    match: terms, phrase, conjunct, fuzzyconjunct
    rank: lengthnorm, psf, proximity, semrichness, termrichness, recency

    filter_ns - filter on namespace, e.g. 'dbpedia'
    '''
    resp = requests.get(LOTUS_API % (match, rank, size, text))
    try:
        concepts = set([hit['subject'] for hit in resp.json()['hits']])

        # filter concepts in particular namespace
        if filter_ns:
            concepts = [concept for concept in concepts if concept.find(filter_ns) > -1]
        
        # recursive call
        if not concepts:
            tokens = text.split(' ')
            # 1st part remove last word
            text = " ".join(tokens[:-1])
            concepts, text = get_concepts_from_lotus(text, filter_ns=filter_ns)
        
        return concepts, text
    except:
        return None, None


def lookup(concept_uri, position='subject'):
    # call ldf
    resp = requests.get(LODALOT_API % (position, concept_uri))
    # print resp.content
    if resp.status_code == requests.codes.ok:
        triples = resp.text.split('\n')[2:]
        return triples


def lookup_nns(concept_uri, position='subject'):
    '''
    lookup nearest neighbours in LOD-a-lot
    collect textual descriptions in English as well 
    '''
    nns_rdf = lookup(concept_uri, position)
    if nns_rdf:
        g = rdflib.Graph()

        for triple in nns_rdf:
            try:
                g.parse(data=triple, format='ntriples')
            except:
                print (triple)

        nns = set()
        descriptions = set()
        for s, p, o in g:
            if type(o) == rdflib.term.URIRef:
                nns.add(str(o.encode('utf-8')))
            # collect English descriptions
            elif type(o) == rdflib.term.Literal and o.language == 'en':
                descriptions.add(str(o))

        return (list(nns), list(descriptions))

    return None, None


def test_babelfy(query=SEED):
    print babelfy_query(query)


def test_lotus(query=SEED):
    lotus_recursive_call(query, filter_ns=False, size=10, verbose=True)


def test_get_concepts(query=SEED):
    concepts = lotus_recursive_call(query, filter_ns=False, size=10, verbose=True)
    if concepts:
        for concept_uris in concepts:
            print (concept_uris)

            # expand concepts
            concepts, descriptions = loop_concept_expansion(concept_uris)
            print (concepts)
            for hop in descriptions:
                for description in hop:
                    print (description)


if __name__ == '__main__':
    test_babelfy()

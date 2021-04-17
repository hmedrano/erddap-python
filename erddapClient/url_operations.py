import os 
from urllib.parse import quote, quote_plus, urlparse, ParseResult

        
def parseQueryItems(items, useSafeURL=True, safe='', item_separator='&'):
    if useSafeURL:
        return quote(item_separator.join(items), safe=safe)
    else:
        return item_separator.join(items)

def url_join(*args):
    return "/".join(map(lambda x: str(x).rstrip('/'), args))

def joinURLElements(base, query):
    return base + '?' + query

def joinURLElementsWithAuth(base, query, auth):
    abase = base.replace("https://", "https://{}:{}@".format(auth[0],auth[1]))
    abase = base.replace("http://", "http://{}:{}@".format(auth[0],auth[1]))
    return joinURLElements(abase, query)



import os 
from urllib.parse import quote, quote_plus, urlparse, ParseResult


#class URLBulder:
#
#    def __init__(self, base, query="", auth=(None,None)):
#        self.baseurl = base
#        self.query = query
#        self.auth = auth
#    
#    def addQueryPair(self, query):
#        if self._urlparseresult.query:
#            self._urlparseresult.query = '&'.join([self._urlparseresult.query, query]) 
#        else:
#            self._urlparseresult.query = query
#    
#    def build(self, includeAuth=False):
#        if includeAuth:
#            return self._urlparseresult.geturl()
#        else:
#            return self._buildWithoutAuth()
#            _authbk = (self._urlparseresult.username, self._urlparseresult.password)
#            self._urlparseresult.username, self._urlparseresult.password = None, None
#    
#    def _buildWithoutAuth(self):
#        _noauthparseresult = self._urlparseresult.copy()
#        _noauthparseresult.username = None
#        _noauthparseresult.password = None
#        return _noauthparseresult.geturl()
        

def parseQueryItems(items, useSafeURL=True, safe='', item_separator='&'):
    if useSafeURL:
        return quote(item_separator.join(items), safe=safe)
    else:
        return item_separator.join(items)

def joinURLElements(base, query):
    return base + '?' + query

def joinURLElementsWithAuth(base, query, auth):
    abase = base.replace("https://", "https://{}:{}@".format(auth[0],auth[1]))
    abase = base.replace("http://", "http://{}:{}@".format(auth[0],auth[1]))
    return joinURLElements(abase, query)



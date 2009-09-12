from logging import debug, error, info
from os import environ
from cgi import parse_qs
from google.appengine.api.memcache import get, set as mset, get_multi
from random import sample

"""
A ntrack tracker
================

Memcached namespaces:

- 'K': Keys / info_hashes -> set of ips (sets have a slight overhead over lists, but are more foolsafe)
- 'I': Client ips -> metadata (currently a tuple with one item: (Port,))
- 'D': Debug data

This allows peer info to be shared and decay by itself, we will delete references to peer from
the key namespace lazily.
"""

required_args = ['info_hash', 'port']

inst_key_cache = {}

DEBUG = True

def resps(s):
    print "Content-type: text/plain"
    print ""
    print s, # Make sure we don't add a trailing new line!

def key2s(k):
    if k:
        return ''.join(["%03X"% ord(c) for c in k])
    else:
        return "NO KEY!"

def main():
    args = parse_qs(environ['QUERY_STRING'])

    if DEBUG:
        dtracks = get('tracks', namespace='D')
        if not dtracks:
            dtracks = set([])
        dpeers = get('peers', namespace='D')
        if not dpeers:
            dpeers = set([])

    if not args:
        if DEBUG:
            resps(repr(inst_key_cache) +"\n"+ repr(dtracks) +"\n"+ repr(dpeers))
        return

    for a in required_args:
        if a not in args or len(args[a]) < 1:
            error("Missing required argument: "+a)
            raise Exception("Missing required argument: "+a )

    key = args['info_hash'][0]
    ip = environ['REMOTE_ADDR']
    port = int(args['port'][0]) # TODO Should catch str->int conversion errors
    # TODO BT: If left=0, the download is done and we should not return any peers.
    # TODO BT: On event=stop should remove peer.
    debug("Requested key %s by %s : %d" % (key2s(key), ip, port))

    updatetrack = False

    # Get existing peers
    s = get(key, namespace='K')

    if s:
        # TODO rate limiting, exponential backoff, etc

        if len(s) > 10:
            ips = set(sample(s, 10))
        else:
            ips = s

        peers = get_multi(ips, namespace='I')

        lostpeers = [p for p in ips if p not in peers]
        if lostpeers: # Remove lost peers
            info("Removed 'lost' peers: "+lostpeers+" from track: "+key) 
            s.difference_update(lostpeers)
            updatetrack = True

        peers.pop(ip, None) # Remove self from list of returned peers

    # New track! Create track with this ip and we are done!
    else:
        s = set([])
        peers = {}

    if DEBUG:
        dpeers.add((ip, port,))
        mset('peers', dpeers, namespace='D')

    mset(ip, (port,), namespace='I') # This might be redundant, but ensures we update the port number in case it has changed.
    if ip not in s: # Assume new peer
        debug("New peer %s port %d" % (ip, port))
        s.add(ip)
        updatetrack = True

    if updatetrack: 
        if DEBUG:
            dtracks.add(tuple(s))
            mset('tracks', dtracks, namespace='D')
        mset(key, s, namespace='K')
        inst_key_cache[key] = s

    # We should try removing the int(<port>), I think it was only needed because memcached was stale with non-int values.
    resps(bencode({'interval': 1024, 'peers': [{'ip': p, 'port': int(peers[p][0])} for p in peers]}))


################################################################################
# Bencode encoding code by Petru Paler, slightly simplified by uriel
from types import StringType, IntType, LongType, DictType, ListType, TupleType, BooleanType

#class Bencached(object):
#    __slots__ = ['bencoded']
#
#    def __init__(self, s):
#        self.bencoded = s

#def encode_bencached(x,r):
#    r.append(x.bencoded)

def encode_int(x, r):
    r.extend(('i', str(x), 'e'))

def encode_string(x, r):
    r.extend((str(len(x)), ':', x))

def encode_list(x, r):
    r.append('l')
    for i in x:
        encode_func[type(i)](i, r)
    r.append('e')

def encode_dict(x,r):
    r.append('d')
    ilist = x.items()
    ilist.sort()
    for k, v in ilist:
        r.extend((str(len(k)), ':', k))
        encode_func[type(v)](v, r)
    r.append('e')

encode_func = {}
#encode_func[type(Bencached(0))] = encode_bencached
encode_func[IntType] = encode_int
encode_func[LongType] = encode_int
encode_func[StringType] = encode_string
encode_func[ListType] = encode_list
encode_func[TupleType] = encode_list
encode_func[DictType] = encode_dict
encode_func[BooleanType] = encode_int

def bencode(x):
    r = []
    encode_func[type(x)](x, r)
    return ''.join(r)

def test_bencode():
    assert bencode(4) == 'i4e'
    assert bencode(0) == 'i0e'
    assert bencode(-10) == 'i-10e'
    assert bencode(12345678901234567890L) == 'i12345678901234567890e'
    assert bencode('') == '0:'
    assert bencode('abc') == '3:abc'
    assert bencode('1234567890') == '10:1234567890'
    assert bencode([]) == 'le'
    assert bencode([1, 2, 3]) == 'li1ei2ei3ee'
    assert bencode([['Alice', 'Bob'], [2, 3]]) == 'll5:Alice3:Bobeli2ei3eee'
    assert bencode({}) == 'de'
    assert bencode({'age': 25, 'eyes': 'blue'}) == 'd3:agei25e4:eyes4:bluee'
    assert bencode({'spam.mp3': {'author': 'Alice', 'length': 100000}}) == 'd8:spam.mp3d6:author5:Alice6:lengthi100000eee'
    #assert bencode(Bencached(bencode(3))) == 'i3e'
    try:
        bencode({1: 'foo'})
    except TypeError:
        return
    assert 0

################################################################################

if __name__ == '__main__':
    main()

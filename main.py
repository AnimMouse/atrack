from logging import debug, error, info
from os import environ
from cgi import parse_qs
from hashlib import md5
from random import sample
from google.appengine.api.memcache import get, set as mset, get_multi, delete as mdel

"""
A ntrack tracker
================

Memcached namespaces:

- 'K': Keys / info_hashes -> String of | delimited peer-hashes
- 'I': peer-hash -> Metadata string: 'ip|port'
- 'D': Debug data

A peer hash is: md5("%s/%d").hexdigest()[:16]

This allows peer info to be shared and decay by itself, we will delete
references to peer from the key namespace lazily.
"""

def resps(s):
    print "Content-type: text/plain"
    print ""
    print s, # Make sure we don't add a trailing new line!

def prof_main():
    # This is the main function for profiling 
    import cProfile, pstats, StringIO
    import logging
    prof = cProfile.Profile()
    prof = prof.runctx("real_main()", globals(), locals())
    stream = StringIO.StringIO()
    stats = pstats.Stats(prof, stream=stream)
    stats.sort_stats("time")  # Or cumulative
    stats.print_stats(80)  # 80 = how many to print
    # The rest is optional.
    # stats.print_callees()
    # stats.print_callers()
    logging.info("Profile data:\n%s", stream.getvalue())


def real_main():
    args = parse_qs(environ['QUERY_STRING'])

    if not args:
        print "Status: 301 Moved Permanantly\nLocation: /\n\n",
        return

    for a in ('info_hash', 'port'):
        if a not in args or len(args[a]) < 1:
            return # Maybe now that trackhub is fixed we shoud be less harsh?
            resps(bencode({'failure reason': "You must provide %s!"%a}))

    ip = environ['REMOTE_ADDR']
    key = args['info_hash'][0]
    err = None

    if(len(key) > 128):
        err = "Insanely long key!"
    else:
        try:
            port = int(args['port'][0])
        except:
            err = "Invalid port number!"

    if err:
        return resps(bencode({'failure reason': err}))

    # Crop raises chance of a clash, plausible deniability for the win!
    phash = md5("%s/%d" % (ip, port)).hexdigest()[:16] 

    # TODO BT: If left=0, the download is done and we should not return any peers.
    event = args.pop('event', [None])[0]
    if event == "stopped":
        # Maybe we should only remove it from this track, but this is good enough.
        mdel(phash, namespace='I')
        return # They are going away, don't waste bw/cpu on this.
        resps(bencode({'interval': 2048, 'peers': []}))

    updatetrack = False

    # Get existing peers
    r = get(key, namespace='K')

    if r:

        s = r.split('|')
        if len(s) > 32:
            ks = sample(s, 32)
        else:
            ks = s

        peers = get_multi(ks, namespace='I')

        lostpeers = (p for p in ks if p not in peers)
        if lostpeers: # Remove lost peers
            s = [k for k in s if k not in lostpeers]
            updatetrack = True

        if phash in peers:
            peers.pop(phash, None) # Remove self from returned peers

    # New track!
    else:
        s = []
        peers = {}

    mset(phash, '|'.join((ip, str(port))), namespace='I') # This might be redundant, but ensures we update the port number in case it has changed.
    if phash not in s: # Assume new peer
        s.append(phash)
        updatetrack = True

    if updatetrack: 
        mset(key, '|'.join(s), namespace='K')

    #debug("Returned %s peers" % len(peers))
    ps = dict((k, peers[k].split('|')) for k in peers)
    pl = [{'ip': ps[h][0], 'port': ps[h][1]} for h in ps]
    resps(bencode({'interval': 4424, 'peers': pl}))

#main = prof_main
main = real_main

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

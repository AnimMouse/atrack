import logging as log
from os import environ
from cgi import parse_qs
from google.appengine.api.memcache import get, set as mset, get_multi
from random import sample

required_args = ['info_hash', 'peer_id', 'port'] # FUTURE: 'port' should be optional

"""
A ntrack tracker
================

Memcached namespaces:

- 'K': Keys / info_hashes -> set of ips (sets have a slight overhead over lists, but are more foolsafe)
- 'I': Client ips -> metadata (currently a tuple with two items: (Peer Id, Port))

This allows peer info to be shared and decay by itself, we will delete references to peer from
the key namespace lazily.


"""

def main():
    args = parse_qs(environ['QUERY_STRING'])

    for a in required_args:
        if a not in args or len(args[a]) < 1:
            log.error("Missing required argument: "+a)
            raise Exception()

    key = args['info_hash'][0]
    peer_id = args['peer_id'][0]
    ip = environ['REMOTE_ADDR']
    port = args['port'][0]

    newpeer = False
    updatetrack = False

    # Get existing peers
    s = get(key, namespace='K')

    if s:
        # TODO rate limiting, exponential backoff, etc

        if len(s) > 10:
            rips = set(sample(s, 10))
        else:
            rips = s

        peers = get_multi(rips, namespace='I')

        lostpeers = [p for p in rips if p not in peers]
        if lostpeers: # Remove lost peers
            s.difference_update(lostpeers)
            rips.difference_update(lostpeers)
            updatetrack = True

        if ip not in s: # Assume new peer
            newpeer = True


    # New track! Create track with this ip and we are done!
    else:
        s = set([ip])
        rips = set([]) # No peers yet!
        newpeer = True # Will also update track

    if newpeer:
        mset(ip, (peer_id, port), namespace='I')
        s.add(ip)
        updatetrack = True

    if updatetrack: 
        mset(key, s, namespace='K')

    print "Content-type: text/plain"
    print ""
    print {'interval': 1024, 'peers': [{'peer id': peers[p][0], 'ip': p, 'port': peers[p][1]} for p in rips]} 

if __name__ == '__main__':
    main()

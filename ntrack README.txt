Ntrack: The Network Tracker protocol
====================================


Ntrack is a simplification and generalization of the bittorrent HTTP tracker protocol.

The aim is to produce a more lean and streamlined protocol that removes bittorrent specific aspects and can be used for any number of peers to associate IP:PORTs to a given key (info_hash in the case of Bittorrent).

The main goals are:

- Simple: retain the simplicity and transparency of textual data, and further simplify the data structures and URL scheme.
- Lean: as bandwidth and computationally efficient as reasonably possible.
- General: Should be useful for any task that requires a bunch of decentralized clients to publish their connection information. 
- Backwards compatible: we don't want to break (too much) existing Bittorrent clients.


Note: this effort almost completely unrelated to the new UDP bittorrent tracker protocol.


Terminology
-----------

- BT: Bittorrent tracker protocol.
- NT: Ntrack tracker protocol.
- Key: An arbitrary UTF-8 string, in BT it is the info_hash.
- Track: A set of IP:PORTs associated with a key.
- Tracker: A server that collects and publishes tracks from and to clients.
- Peer: A client that connects to a tracker to publish its connection information to a given track and retrieve the connection information of other peers in the track.


Changes from BT
---------------

Proposed backwards compatible Changes from the BT tracking protocol:

- 'info_hash' is an arbitrary string (ie., a key).
- 'peer_id' is optional, if omitted for backwards compatibility purposes it can be generated as the sha1 hash of IP:PORT. [XXX]
- 'ip' is deprecated and can be ignored, always use the HTTP client's ip. [XXX]
- 'port' is optional, if missing use the port of origin of the HTTP connection.
- 'uploaded', 'downloaded' and 'left' can be ignored.
- The semantics of 'event' are ambiguous and bittorrent specific enough that it can be safely ignored. [XXX]


New ntrack REST-ful interface
-----------------------------

A ntracker serves by convention under /ntrk/, so only an ip or domain, and no full url is needed to refer to the ntracker.

An HTTP GET request from IP 123.45.67.89 and port 1234 to the URL:

	http://myntracker.com/ntrk/MYKEY

Is equivalent to this request in the classic BT tracker protocol:

	http://mybttracker.com/tracker?info_hash=MYKEY&peer_id=396747a010eff799e3a82ce1b351ac25bce23fce&port=1234


Open issues
-----------

They are marked with [XXX] in the text of this document. 

- Is the Peer ID generation from the IP:PORT hash good enough? Is it too long? What exactly is its purpose in BT?
- Should set Peer ID and Key length limits.
- Not sure what the 'ip' query string parameter was really for and if we can safely deprecate it.
- Similar possible issues with 'uploaded', 'downloaded', 'left', and 'event'.
- Maybe we need something like 'event' but with better defined semantics, so peers can easily remove themselves from the list and so on.


Related protocols
-----------------

One could think of ntrack as a centralized, dynamically updated, and extremely simplified DNS system.

Ntrack is compatible with [the HTTP 0.2 subset of HTTP](<http://http02.cat-v.org).


Possible uses
-------------

- Online games
- Chat systems 
- Distributed computing


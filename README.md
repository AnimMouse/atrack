# Atrack Torrent Tracker

Atrack is a Bittorrent tracker designed from the ground up to run on [Google’s App Engine](https://cloud.google.com/appengine/) grid.

Atrack is based on the abandoned [Atrack](http://repo.cat-v.org/atrack/) by [Uriel †](https://github.com/uriel).

## Features
1. It uses memcache to store IP addresses, ports, and hashes/keys.
2. It uses [ntrack](http://repo.cat-v.org/atrack/ntrack), the Network Tracker protocol.
3. It is a torrent tracker running in Google's fast servers.
4. It also aims to respect your privacy, other than what is needed for the most basic tracking (hashes/keys and IP/ports), atrack gathers no information whatsoever.

## Installation
This tutorial uses the original App Engine SDK instead of the new Google Cloud SDK.

Make sure you have a Google Account and created an application inside a project in Google Cloud Console.
1. Clone or Download the latest source [here](https://github.com/AnimMouse/atrack/archive/master.zip).
2. Download the Google Cloud SDK [here](https://cloud.google.com/sdk/docs)
3. Deploy the instance by typing this command `gcloud app deploy -v 1` inside the instance folder

## Contributing

Feel free to make suggestions, create pull requests, report issues or any other feedback.

Contact us on contact@atrack.eu.org

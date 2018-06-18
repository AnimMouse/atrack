# Atrack Torrent Tracker

Atrack is a [ntrack](http://repo.cat-v.org/atrack/ntrack) / Bittorrent tracker designed from the ground up to run on [Google’s App Engine](https://cloud.google.com/appengine/) grid.

Atrack is based on the abandoned [Atrack](http://repo.cat-v.org/atrack/) by [Uriel †](https://github.com/uriel).

## Installation
1. Clone the repo
2. Get the original App Engine SDK [here](https://cloud.google.com/appengine/docs/standard/php/download) (use PHP SDK instead of Python SDK because PHP also contains Python, but not vise versa.)
3. Temporarily move away dispatch.yaml from default, because it will fail because you haven't deployed the modules (aka services) yet.
4. Deploy default
5. Deploy instance-1
6. Deploy instance-2
7. Deploy redirect
8. Put dispatch.yaml inside default and deploy again
9. Finished.
Note: Installation is based on my configuration, change it for you.

## Contributors

Feel free to make suggestions, create pull requests, report issues or any other feedback.

Contact me here.

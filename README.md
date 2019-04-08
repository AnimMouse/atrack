# Atrack Torrent Tracker

Atrack is a [ntrack](http://repo.cat-v.org/atrack/ntrack) / Bittorrent tracker designed from the ground up to run on [Google’s App Engine](https://cloud.google.com/appengine/) grid.

Atrack is based on the abandoned [Atrack](http://repo.cat-v.org/atrack/) by [Uriel †](https://github.com/uriel).

## Features
1. It uses memcache to store IP addresses, ports, and hashes/keys.
2. It uses the ntrack protocol.
3. It is an tracker in Google's servers.

## Installation
Make sure you have a Google Account and created an application inside a project in Google Cloud Console.
1. Download the release [here](https://github.com/AnimMouse/atrack/releases/download/v0.9.11/Atrack.7z).
2. Get the original App Engine SDK [here](https://cloud.google.com/appengine/docs/standard/php/download) (use PHP SDK instead of Python SDK because PHP also contains Python, but not vise versa.)
3. Temporarily move away dispatch.yaml inside the default folder, because it will fail because you haven't deployed the modules (aka services) yet.
4. Change the configurations inside the "app.yaml" in each of the services. Inside the app.yaml file, there is a setting named "application-name", change it to the app ID or the application name you created in Google Cloud Console.
5. Change the configurations inside the "dispatch.yaml" for custom domain redirection.
6. Deploy the default service by adding the folder inside App Engine SDK and clicking deploy. If you aren't already entered your Google Credentials, you will be prompted to enter.
7. Just like step 6, deploy instance-1 by adding the folder inside App Engine SDK and clicking deploy.
8. Just like step 6, deploy redirect by adding the folder inside App Engine SDK and clicking deploy.
9. Put dispatch.yaml inside the default and deploy again the default folder just like in step 6.
10. Finished.

## Contributing

Feel free to make suggestions, create pull requests, report issues or any other feedback.

Contact us on contact@atrack.eu.org

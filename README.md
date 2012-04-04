=====================
 Trakt To Plex syncer
=====================

This script connects to Trakt.tv and reports the watched content to a Plex media center server based on [jone / plex-trakt-syncer](https://github.com/jone/plex-trakt-syncer)
Not likely to be used often however if you ever need to wipe out your Plex library it may come in handy.

Features
========

- Currently only marks **show episodes** watched in [Plex](http://www.plexapp.com/) when watched in your [Trakt](http://trakt.tv) profile.


Usage
=====

.. %usage-start%

::

    Usage: plex-trakt-sync.py [options]

    This script connects to Trakt.tv and reports the watched content to a Plex media center server

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -H HOST, --host=HOST  Hostname or IP of plex server (default: localhost)
      -P PORT, --port=PORT  Port of the plex server (default: 32400)
      -u USERNAME, --username=USERNAME
                            trakt.tv username
      -p PASSWORD, --password=PASSWORD
                            trakt.tv password
      -k API-KEY, --key=API-KEY
                            trakt.tv API key
      -v, --verbose         Print more verbose debugging informations.

.. %usage-end%
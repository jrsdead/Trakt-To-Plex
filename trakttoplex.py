#!/usr/bin/env python

from optparse import OptionParser
import json
import xml.etree.ElementTree as ET
import logging
import os
import sys
import urllib
import urllib2


VERSION = '1.0'

DESCRIPTION = '''This script connects to Trakt.tv and
reports the watched content to a Plex media center server.'''

EPILOG = '''

'''

LOG_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)),
    'TraktToPlex.log')

logging.basicConfig(
    filename=LOG_FILE,
    datefmt='%Y-%m-%dT%H:%M:%S',
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s')


LOG = logging.getLogger('trakttoplex')
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.INFO)


class TraktToPlex(object):

    def __call__(self, args=None):
        if args is None:
            args = sys.argv[1:]

        self.parse_arguments(args)
        self.sync_shows()

    def quit_with_error(self, message):
        LOG.error(message)
        sys.exit(1)

    def parse_arguments(self, args):
        """Parses the passed arguments.
        """

        parser = OptionParser(version=VERSION, description=DESCRIPTION,
            epilog=EPILOG)

        parser.add_option(
            '-H', '--host', dest='plex_host', default='localhost',
            metavar='HOST',
            help='Hostname or IP of plex server (default: localhost)')

        parser.add_option(
            '-P', '--port', dest='plex_port', default=32400,
            metavar='PORT',
            help='Port of the plex server (default: 32400)')

        parser.add_option(
            '-u', '--username', dest='trakt_username',
            metavar='USERNAME',
            help='trakt.tv username')

        parser.add_option(
            '-p', '--password', dest='trakt_password',
            metavar='PASSWORD',
            help='trakt.tv password')

        parser.add_option(
            '-k', '--key', dest='trakt_key',
            metavar='API-KEY',
            help='trakt.tv API key')

        parser.add_option(
            '-v', '--verbose', dest='verbose', action='store_true',
            help='Print more verbose debugging informations.')

        self.options, self.arguments = parser.parse_args(args)

        if self.options.verbose:
            LOG.setLevel(logging.DEBUG)

        # validate options
        if not self.options.trakt_username:
            self.quit_with_error('Please define a trakt username (-u).')

        if not self.options.trakt_key:
            self.quit_with_error('Please define a trakt API key (-k).')

        if not self.options.trakt_password:
            self.quit_with_error('Please define a trakt password (-p).')

    def sync_shows(self):
            self.update_plex_shows(self.trakt_get_watched_episodes())

    def update_plex_shows(self, trakt_shows):
        for section_path in self._get_plex_section_paths('show'):
            shows = self._plex_request(section_path + '/all').findall('Directory')
            for show in shows:
                episodes = self._plex_request('/library/metadata/%s/allLeaves' %show.get('ratingKey')).findall('Video')
                for episode in episodes:
                    if episode.get('grandparentTitle') in trakt_shows:
                        show = trakt_shows[episode.get('grandparentTitle')]
                        if int(episode.get('parentIndex')) in show:
                            LOG.info('Found %s Season %s Episode %s' %(episode.get('grandparentTitle'), episode.get('parentIndex'), episode.get('index')))
                            if int(episode.get('index')) in show[int(episode.get('parentIndex'))]:
                                self._plex_request('/:/scrobble?identifier=com.plexapp.plugins.library&key=' + episode.get('ratingKey'), 0)
                                LOG.info('Marked %s Season %s Episode %s as watched in the PMS' %(episode.get('grandparentTitle'), episode.get('parentIndex'), episode.get('index')))
                            else:
                                LOG.info('%s Season %s Episode %s has not been watched' %(episode.get('grandparentTitle'), episode.get('parentIndex'), episode.get('index')))


    def trakt_get_watched_episodes(self):
        url = 'http://api.trakt.tv/user/library/shows/watched.json/%s/%s' % (self.options.trakt_key, self.options.trakt_username)
        LOG.info('Getting data from trakt.tv for username:%s' %self.options.trakt_username)
        try:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)

        except urllib2.URLError, e:
            LOG.error(e)
            raise

        resp_data = response.read()
        resp_json = json.loads(resp_data)

        shows_from_trakt = {}

        for show in resp_json:
            #LOG.info('%s\n' %item)
            shows_from_trakt[show.get('title')] = {}
            for season in show.get('seasons'):
                shows_from_trakt[show.get('title')][season.get('season')] = season.get('episodes')
        return shows_from_trakt

    def _get_plex_section_paths(self, type_):
        """Returns all paths to sections of a particular type.
        _get_plex_section_paths('movie') => ['/library/sections/1/']
        """

        sections_path = '/library/sections'
        paths = []

        tree = self._plex_request(sections_path)
        for dir in tree.findall('Directory'):
            if dir.get('type') == type_:
                paths.append('%s/%s' %(sections_path,dir.get('key')))

        return paths


    def _plex_request(self, path, passback=1):
        url = 'http://%s:%s%s' % (
            self.options.plex_host,
            self.options.plex_port,
            path)

        LOG.debug('Plex request to %s' % url)

        try:
            response = urllib.urlopen(url)
            if passback == 1:
                data = response.read()
                tree = ET.fromstring(data)
                return tree
        except IOError, e:
            LOG.error(str(e))
            sys.exit()

if __name__ == '__main__':
    try:
        TraktToPlex()()
    except Exception, e:
        LOG.error(str(e))
        raise
"""
    urlresolver XBMC Addon
    Copyright (C) 2015 tknorris

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
from lib import aa_decoder
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class VideowoodResolver(UrlResolver):
    name = "videowood"
    domains = ['videowood.tv']
    pattern = '(?://|\.)(videowood\.tv)/(?:embed/|video/)([0-9a-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'Referer': web_url, 'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        try: html = html.encode('utf-8')
        except: pass
        if "This video doesn't exist." in html:
            raise ResolverError('The requested video was not found.')
        
        match = re.search("split\('\|'\)\)\)\s*(.*?)</script>", html)
        if match:
            aa_text = aa_decoder.AADecoder(match.group(1)).decode()
            match = re.search("'([^']+)", aa_text)
            if match:
                stream_url = match.group(1)
                return stream_url + '|User-Agent=%s' % (common.FF_USER_AGENT)
        
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return 'http://videowood.tv/embed/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host

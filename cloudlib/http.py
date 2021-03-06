# Copyright 2015, Kevin Carter.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Example Usage:
>>> from cloudlib import http
>>> make_req = http.MakeRequest()
>>> get_req = make_req.get('https://api.github.com/orgs/openstack')
"""

import sys
import urllib


# Added for python3 support
try:
    import httplib
except ImportError:
    import http.client as httplib

# Added for python3 support
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import requests

from cloudlib import logger
from cloudlib import utils


def parse_url(url):
    """Return a clean URL. Remove the prefix for the Auth URL if Found.

    :param url:
    :return aurl:
    """
    if url.startswith(('http', 'https', '//')):
        if url.startswith('//'):
            return urlparse.urlparse(url, scheme='http')
        else:
            return urlparse.urlparse(url)
    else:
        return urlparse.urlparse(urlparse.urljoin('http://', url))


def html_encode(path):
    """Return an HTML encoded Path.

    :param path: ``str``
    :return: ``str``
    """
    if sys.version_info > (3, 2, 0):
        return urllib.parse.quote(utils.ensure_string(path))
    else:
        return urllib.quote(utils.ensure_string(path))


class MakeRequest(object):

    def __init__(self, config=None, log_name=__name__):
        """Make an HTTP request.

        This class allows you to create custom request args and or enable
        debug mode.

        Presently the ``config`` argument would only be used to enable
        debug.

        :param config: ``dict``
        :param log_name: ``str`` This is used to log against an existing log
                                 handler.
        """

        self.config = config
        if self.config is None:
            self.config = {}

        self.log = logger.getLogger(log_name)
        self.request_kwargs = {'timeout': self.config.get('timeout', 60)}
        self.headers = {
            'User-Agent': 'cloudlib'
        }

        if isinstance(self.config, dict):
            if 'headers'in self.config:
                self.headers.update(self.config.get('headers'))

            if self.config.get('debug', False):
                httplib.HTTPConnection.debuglevel = 1

    @staticmethod
    def _get_url(url):
        """Returns a URL string.

        If the ``url`` parameter is a ParsedResult from `urlparse` the full url
        will be unparsed and made into a string. Otherwise the ``url``
        parameter is returned as is.

        :param url: ``str`` || ``object``
        """
        if isinstance(url, urlparse.ParseResult):
            return urlparse.urlunparse(url)
        else:
            return url

    def _report_error(self, request, exp):
        """When making the request, if an error happens, log it."""
        message = (
            "Failure to perform %s due to [ %s ]" % (request, exp)
        )
        self.log.fatal(message)
        raise requests.RequestException(message)

    def _request(self, method, url, headers=None, body=None, kwargs=None):
        """Make a request.

        To make a request pass the ``method`` and the ``url``. Valid methods
        are, ``['post', 'put', 'get', 'delete', 'patch', 'option', 'head']``.

        :param url: ``str``
        :param headers: ``dict``
        :param body: ``object``
        :param kwargs: ``dict``
        """
        _kwargs = utils.dict_update(self.request_kwargs.copy(), kwargs)
        _headers = utils.dict_update(self.headers.copy(), headers)
        _url = self._get_url(url=url)

        try:
            func = getattr(requests, method.lower())
            if body is None:
                resp = func(_url, headers=_headers, **_kwargs)
            else:
                resp = func(_url, data=body, headers=_headers, **_kwargs)
            self.log.debug(
                '%s %s %s', resp.status_code, resp.reason, resp.request
            )
        except AttributeError as exp:
            self._report_error(request=method.upper(), exp=exp)
        else:
            return resp

    def post(self, url, headers=None, body=None, kwargs=None):
        """Make a POST request.

        To make a POST request pass, ``url``

        :param url: ``str``
        :param headers: ``dict``
        :param body: ``object``
        :param kwargs: ``dict``
        """
        return self._request(
            method='post',
            url=url,
            headers=headers,
            body=body,
            kwargs=kwargs
        )

    def head(self, url, headers=None, kwargs=None):
        """Make a HEAD request.

        To make a HEAD request pass, ``url``

        :param url: ``str``
        :param headers: ``dict``
        :param kwargs: ``dict``
        """
        return self._request(
            method='head',
            url=url,
            headers=headers,
            kwargs=kwargs
        )

    def patch(self, url, headers=None, body=None, kwargs=None):
        """Make a PATCH request.

        To make a PATCH request pass, ``url``

        :param url: ``str``
        :param headers: ``dict``
        :param body: ``object``
        :param kwargs: ``dict``
        """
        return self._request(
            method='patch',
            url=url,
            headers=headers,
            body=body,
            kwargs=kwargs
        )

    def put(self, url, headers=None, body=None, kwargs=None):
        """Make a PUT request.

        To make a PUT request pass, ``url``

        :param url: ``str``
        :param headers: ``dict``
        :param body: ``object``
        :param kwargs: ``dict``
        """
        return self._request(
            method='put',
            url=url,
            headers=headers,
            body=body,
            kwargs=kwargs
        )

    def delete(self, url, headers=None, kwargs=None):
        """Make a DELETE request.

        To make a DELETE request pass, ``url``

        :param url: ``str``
        :param headers: ``dict``
        :param kwargs: ``dict``
        """
        return self._request(
            method='delete',
            url=url,
            headers=headers,
            kwargs=kwargs
        )

    def get(self, url, headers=None, kwargs=None):
        """Make a GET request.

        To make a GET request pass, ``url``

        :param url: ``str``
        :param headers: ``dict``
        :param kwargs: ``dict``
        """
        return self._request(
            method='get',
            url=url,
            headers=headers,
            kwargs=kwargs
        )

    def option(self, url, headers=None, kwargs=None):
        """Make a OPTION request.

        To make a OPTION request pass, ``url``

        :param url: ``str``
        :param headers: ``dict``
        :param kwargs: ``dict``
        """
        return self._request(
            method='option',
            url=url,
            headers=headers,
            kwargs=kwargs
        )

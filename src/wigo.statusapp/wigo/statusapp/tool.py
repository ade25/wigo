import json
import socket
import requests
import contextlib
import smtplib
from urllib import urlencode
from urllib2 import urlopen
from urllib2 import HTTPError
from five import grok
from plone import api
from zope.interface import Interface


DEFAULT_SERVICE = 'http'
DEFAULT_SERVICE_URI = 'serverdetails.json'
DEFAULT_SERVICE_TIMEOUT = socket.getdefaulttimeout()


class IWigoTool(Interface):
    """ Call processing and optional session data storage entrypoint """

    def status(context):
        """ Check availability of external service

        @param timeout: Set status request timeout
        @param service: Service type e.g. tcp
        @param host:    Hostname of the component node
        @param payload: Pass additional parameters e.g. auth tokens
        """


class WigoTool(grok.GlobalUtility):
    grok.provides(IWigoTool)

    def status(self,
               hostname=None,
               service=DEFAULT_SERVICE,
               timeout=DEFAULT_SERVICE_TIMEOUT,
               **kwargs):
        info = {}
        info['name'] = service
        if service == 'smtp':
            smtp = smtplib.SMTP()
            response = smtp.connect(hostname)
            info['code'] = response[0]
            info['status'] = 'active'
        else:
            url = 'http://{0}'.format(hostname)
            with contextlib.closing(requests.get(url)) as response:
                r = response
                sc = r.status_code
                info['code'] = sc
                if sc == requests.codes.ok:
                    info['status'] = 'active'
                else:
                    info['code'] = 'unreachable endpoint'
        return info

    def get(self,
            hostname=None,
            path_info=DEFAULT_SERVICE_URI,
            timeout=DEFAULT_SERVICE_TIMEOUT, **kwargs):
        service_url = 'http://{0}'.format(hostname)
        url = service_url + '/{0}'.format(path_info)
        with contextlib.closing(requests.get(url)) as response:
            r = response
            if r.status_code == requests.codes.ok:
                return r.json()


class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.current_keys, self.past_keys = [
            set(d.keys()) for d in (current_dict, past_dict)
        ]
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        return self.current_keys - self.intersect

    def removed(self):
        return self.past_keys - self.intersect

    def changed(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])

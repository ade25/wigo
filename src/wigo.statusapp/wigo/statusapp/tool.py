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
from plone.event.utils import is_date
from plone.event.utils import is_datetime
from plone.event.utils import is_same_day
from plone.event.utils import is_same_time


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

    def construct_calendar(events, start=None, end=None):
        """Return a dictionary with dates in a given timeframe as keys and the
        actual occurrences for that date for building calendars.
        Long lasting events will occur on every day until their end.

        :param events: List of IEvent and/or IOccurrence objects, to construct a
                       calendar data structure from.
        :type events: list

        :param start: An optional start range date.
        :type start: Python datetime or date

        :param end: An optional start range date.
        :type end: Python datetime or date

        :returns: Dictionary with isoformat date strings as keys and event
                  occurrences as values.
        :rtype: dict

        """
        if start:
            if is_datetime(start):
                start = start.date()
            assert is_date(start)
        if end:
            if is_datetime(end):
                end = end.date()
            assert is_date(end)
        cal = {}

        def _add_to_cal(cal_data, event, date):
            date_str = date.isoformat()
            if date_str not in cal_data:
                cal_data[date_str] = [event]
            else:
                cal_data[date_str].append(event)
            return cal_data

        for event in events:
            acc = IEventAccessor(event)
            start_date = acc.start.date()
            end_date = acc.end.date()
            # day span between start and end + 1 for the initial date
            range_days = (end_date - start_date).days + 1
            for add_day in range(range_days):
                next_start_date = start_date + timedelta(add_day) # initial = 0
                # avoid long loops
                if start and end_date < start:
                    break  # if the date is completly outside the range
                if start and next_start_date <= start:
                    continue  # if start is outside but end reaches into range
                if end and next_start_date > end:
                    break  # if date is outside range

                _add_to_cal(cal, event, next_start_date)
        return cal


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

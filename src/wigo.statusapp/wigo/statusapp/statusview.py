import socket
from Acquisition import aq_inner
from datetime import datetime
from datetime import timedelta
from five import grok
from plone import api

from zope.component import getUtility
from zope.schema.vocabulary import getVocabularyRegistry

from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.contentlisting.interfaces import IContentListing

from wigo.statusapp.tool import IWigoTool
from wigo.statusapp.component import IComponent
from wigo.statusapp.servernode import IServerNode
from wigo.statusapp.incidentrecord import IIncidentRecord


ACCESS_TOKEN = '8ffd1588-648c-4ac9-a1eb-adb6eef9c632'


class StatusView(grok.View):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('status-quo')

    def update(self):
        self.has_components = len(self.available_components()) > 0

    def available_components(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IComponent.__identifier__,
                        review_state='published')
        results = IContentListing(items)
        return results

    def prettify_status(self, status):
        context = aq_inner(self.context)
        registry = getVocabularyRegistry()
        vocabulary = registry.get(context, 'wigo.statusapp.ComponentStatus')
        term = vocabulary.getTerm(status)
        info = {}
        info['title'] = term.title
        info['value'] = term.value
        return info

    def rendering_timestamp(self):
        now = datetime.now()
        return now.isoformat()

    def build_calendar(self):
        tool = getUtility(IWigoTool)
        today = datetime.now()
        twoweeks = timedelta(days=14)
        end = today - twoweeks
        timespan = {}
        for x in range(14):
            delta = timedelta(days=x)
            timespan[x] = today - delta
        cal = tool.construct_calendar(self.recorded_incidents(), today, end)
        return cal

    def recorded_incidents(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IIncidentRecord.__identifier__,
                        sort_on='modified',
                        sort_order='reverse',
                        limit=50)[:50]
        return IContentListing(items)


class RosterStatus(grok.View):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('roster')

    def update(self):
        self.valid_request = self.has_valid_token()
        self.has_contents = len(self.nodes()) > 0

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    def is_equal(self, a, b):
        """ Constant time comparison """
        if len(a) != len(b):
            return False
        result = 0
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)
        return result == 0

    def get_access_token(self):
        key = 'hph.membership.interfaces.IHPHMembershipSettings.api_token'
        return api.portal.get_registry_record(key)

    def has_valid_token(self):
        if not self.traverse_subpath:
            return False
        token = self.subpath[0]
        # stored_token = self.get_access_token()
        stored_token = ACCESS_TOKEN
        if stored_token is None:
            return False
        return self.is_equal(stored_token, token)

    def nodes(self):
        portal = api.portal.get()
        context = portal['sqa']['hosted-pages']
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IServerNode.__identifier__,
                        path=dict(query='/'.join(context.getPhysicalPath()),
                                  depth=1),
                        sort_on='getObjPositionInParent')
        results = IContentListing(items)
        return results

    def resolve_node_ip(self, node):
        nodename = getattr(node, 'server')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((nodename, 0))
        s.getsockname()[0]
        return socket.gethostbyname(socket.gethostname())

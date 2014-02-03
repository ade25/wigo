from Acquisition import aq_inner
from dateutil import rrule
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
from wigo.statusapp.incidentrecord import IIncidentRecord


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
        return now

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

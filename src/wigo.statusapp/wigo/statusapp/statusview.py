from datetime import datetime
from five import grok
from plone import api

from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.contentlisting.interfaces import IContentListing

from wigo.statusapp.component import IComponent


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

    def rendering_timestamp(self):
        now = datetime.now()
        return now

from five import grok
from plone import api

from plone.dexterity.content import Container

from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable

from plone.app.contentlisting.interfaces import IContentListing
from wigo.statusapp.incident import IIncident

from wigo.statusapp import MessageFactory as _


class IIncidentManager(form.Schema, IImageScaleTraversable):
    """
    Container holding incidents and providing a history view
    """


class IncidentManager(Container):
    grok.implements(IIncidentManager)

    # Add your class methods and properties here
    pass


class View(grok.View):
    grok.context(IIncidentManager)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        self.has_incidents = len(self.incidents()) > 0

    def incidents(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IIncident.__identifier__,
                        sort_on='getObjPositionInParent')
        results = IContentListing(items)
        return results

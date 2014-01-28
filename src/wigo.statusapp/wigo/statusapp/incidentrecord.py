from five import grok
from zope import schema
from plone.directives import form
from plone.dexterity.content import Item
from plone.namedfile.interfaces import IImageScaleTraversable

from wigo.statusapp import MessageFactory as _


class IIncidentRecord(form.Schema, IImageScaleTraversable):
    """
    A single status message with timestamp to track progress
    """
    status = schema.TextLine(
        title=_(u"Status"),
        required=False
    )


class IncidentRecord(Item):
    grok.implements(IIncidentRecord)
    pass


class View(grok.View):
    grok.context(IIncidentRecord)
    grok.require('zope2.View')
    grok.name('view')

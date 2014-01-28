from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.content import Container

from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable


from wigo.statusapp import MessageFactory as _


class StartBeforeEnd(Invalid):
    __doc__ = _(u"The start or end date is invalid")


class IMaintenance(form.Schema, IImageScaleTraversable):
    """
    Scheduled maintenance timeframe and notifications
    """
    start = schema.Datetime(
        title=_(u"Start date"),
        required=False,
    )

    end = schema.Datetime(
        title=_(u"End date"),
        required=False,
    )

    @invariant
    def validateStartEnd(data):
        if data.start is not None and data.end is not None:
            if data.start > data.end:
                raise StartBeforeEnd(
                    _(u"The start date must be before the end date."))


class Maintenance(Container):
    grok.implements(IMaintenance)
    pass


class View(grok.View):
    grok.context(IMaintenance)
    grok.require('zope2.View')
    grok.name('view')

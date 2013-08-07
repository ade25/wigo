from Acquisition import aq_inner
from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.content import Container
from plone.directives import dexterity, form
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.supermodel import model

from plone.app.textfield import RichText


from wigo.statusapp import MessageFactory as _


# Interface class; used to define content-type schema.

class IStatusApp(model.Schema, IImageScaleTraversable):
    """
    A collection of server status information
    """


class StatusApp(Container):
    grok.implements(IStatusApp)


class View(grok.View):
    """ sample view class """

    grok.context(IStatusApp)
    grok.require('zope2.View')
    grok.name('view')

    def contained_nodes(self):
        context = aq_inner(self.context)
        items = context.restrictedTraverse('@@folderListing')()
        return items

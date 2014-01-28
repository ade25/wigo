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

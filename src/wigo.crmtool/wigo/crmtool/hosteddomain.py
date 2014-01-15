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

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder


from wigo.crmtool import MessageFactory as _


class IHostedDomain(form.Schema, IImageScaleTraversable):
    """
    A single hoted domain that can be accounted for
    """
    link = schema.URI(
        title=_(u"Domain URI"),
        description=_(u"Enter valid remote location"),
        required=True,
    )


class HostedDomain(Container):
    grok.implements(IHostedDomain)


class View(grok.View):
    grok.context(IHostedDomain)
    grok.require('zope2.View')
    grok.name('view')

from Acquisition import aq_inner
from five import grok
from plone import api

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


class IComponent(form.Schema, IImageScaleTraversable):
    """
    A collection of services and associated server nodes
    """
    status = schema.Choice(
        title=_(u"Component Status"),
        description=_(u"Switch component status to signal outages on the "
                      u"public status page."),
        vocabulary=u"wigo.statusapp.ComponentStatus",
        default='operational',
        required=True,
    )


class Component(Container):
    grok.implements(IComponent)


class View(grok.View):
    grok.context(IComponent)
    grok.require('zope2.View')
    grok.name('view')

    def is_public_rouster(self):
        public = False
        if self.get_workflow_state() is True:
            public = True
        return public

    def get_workflow_state(self):
        context = aq_inner(self.context)
        state = api.content.get_state(obj=context)
        return state

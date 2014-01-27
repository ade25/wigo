from AccessControl import Unauthorized
from Acquisition import aq_inner
from five import grok
from plone import api

from zope.component import getMultiAdapter
from plone.keyring import django_random
from zope.schema.vocabulary import getVocabularyRegistry

from plone.dexterity.content import Container
from plone.directives import dexterity
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.supermodel import model

from Products.CMFPlone.utils import safe_unicode
from plone.app.contentlisting.interfaces import IContentListing
from wigo.statusapp.component import IComponent

from wigo.statusapp import MessageFactory as _


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

    def update(self):
        context = aq_inner(self.context)
        self.errors = {}
        unwanted = ('_authenticator', 'form.button.Submit')
        required = ('title')
        if 'form.button.Submit' in self.request:
            authenticator = getMultiAdapter((context, self.request),
                                            name=u"authenticator")
            if not authenticator.verify():
                raise Unauthorized
            form = self.request.form
            form_data = {}
            form_errors = {}
            errorIdx = 0
            for value in form:
                if value not in unwanted:
                    form_data[value] = safe_unicode(form[value])
                    if not form[value] and value in required:
                        error = {}
                        error['active'] = True
                        error['msg'] = _(u"This field is required")
                        form_errors[value] = error
                        errorIdx += 1
                    else:
                        error = {}
                        error['active'] = False
                        error['msg'] = form[value]
                        form_errors[value] = error
            if errorIdx > 0:
                self.errors = form_errors
            else:
                self._create_incident(form)

    def default_value(self, error):
        value = ''
        if error['active'] is False:
            value = error['msg']
        return value

    def _create_incident(self, data):
        context = aq_inner(self.context)
        new_title = data['title']
        token = django_random.get_random_string(length=12)
        api.content.create(
            type='wigo.statusapp.incident',
            id=token,
            title=new_title,
            container=context,
            safe_id=True
        )
        url = context.absolute_url()
        return self.request.response.redirect(url)

    def component_statuses(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IComponent.__identifier__,
                        sort_on='getObjPositionInParent')
        results = IContentListing(items)
        return results

    def status_info(self, uuid):
        vocabulary = self.status_vocabulary()
        item = api.content.get(UID=uuid)
        data = []
        current = getattr(item, 'status', None)
        for item in vocabulary:
            info = item
            active = False
            if item['value'] == current:
                active = True
            info['active'] = active
            data.append(info)
        return data

    def status_vocabulary(self):
        context = aq_inner(self.context)
        registry = getVocabularyRegistry()
        vocabulary = registry.get(context, 'wigo.statusapp.ComponentStatus')
        data = []
        for term in vocabulary:
            info = {}
            info['title'] = term.title
            info['value'] = term.value
            data.append(info)
        return data

    def contained_nodes(self):
        context = aq_inner(self.context)
        items = context.restrictedTraverse('@@folderListing')()
        return items

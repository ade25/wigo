from five import grok
from plone import api
from zope.component import getMultiAdapter

from plone.app.layout.viewlets.interfaces import IPortalFooter
from Products.CMFCore.interfaces import IContentish


class Infobar(grok.Viewlet):
    grok.context(IContentish)
    grok.require('cmf.ModifyPortalContent')
    grok.viewletmanager(IPortalFooter)
    grok.name('wigo.statusapp.InfobarViewlet')

    def update(self):
        self.anonymous = api.user.is_anonymous()
        self.portal_url = api.portal.get().absolute_url()
        self.context_state = self.get_multi_adapter(u'plone_context_state')

    def get_multi_adapter(self, name):
        return getMultiAdapter((self.context, self.request), name=name)

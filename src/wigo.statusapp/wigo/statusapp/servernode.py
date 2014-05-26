import json
import urllib2
from Acquisition import aq_inner
from five import grok

from zope import schema
from zope.component import getUtility
from zope.lifecycleevent import modified

from plone.dexterity.content import Container
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.supermodel import model
from plone.directives import form

from Products.statusmessages.interfaces import IStatusMessage
from wigo.statusapp.tool import IWigoTool

from wigo.statusapp import MessageFactory as _


class IServerNode(model.Schema, IImageScaleTraversable):
    """
    Server details
    """
    server = schema.TextLine(
        title=_(u"Server Name"),
        description=_(u"Enter a fully qualified servername"),
        required=True
    )
    machine = schema.TextLine(
        title=_(u"Physical Server"),
        description=_(u"name of the physical machine this virtual server "
                      u"is located on"),
        required=False,
    )
    protocol = schema.TextLine(
        title=_(u"Request Protocol"),
        description=_(u"Specify alternative protocol e.g. smtp for mx server"),
        default=u"http",
        required=True
    )
    form.mode(serverdetails='hidden')
    serverdetails = schema.TextLine(
        title=_(u"server Details"),
        description=_(u"Serverdetails json storage. You normally should have "
                      u"no need to change this manually"),
        required=False,
    )


class ServerNode(Container):
    grok.implements(IServerNode)


class View(grok.View):
    """ sample view class """

    grok.context(IServerNode)
    grok.require('zope2.View')
    grok.name('view')

    def check_server_status(self):
        host = getattr(self.context, 'server')
        protocol = getattr(self.context, 'protocol', 'http')
        tool = getUtility(IWigoTool)
        status = tool.status(hostname=host, service=protocol)
        return status


class ServerDetails(grok.View):
    grok.context(IServerNode)
    grok.require('cmf.ModifyPortalContent')
    grok.name('update-serverdetails')

    def render(self):
        context = aq_inner(self.context)
        tool = getUtility(IWigoTool)
        hostname = getattr(context, 'server', '')
        if hostname is not None:
            data = tool.get(hostname=hostname)
            setattr(context, 'serverdetails', data)
            modified(context)
            context.reindexObject(idxs='modified')
            IStatusMessage(self.request).addStatusMessage(
                _(u"The panel has successfully been updated"),
                type='info')
            next_url = context.absolute_url()
            return self.request.response.redirect(next_url)

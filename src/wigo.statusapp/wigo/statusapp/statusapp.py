# -*- coding: utf-8 -*-
"""Module providing status app overview and cluster storage"""

import datetime
import time
import json

import uuid as uuid_tool

from AccessControl import Unauthorized
from Acquisition import aq_inner
from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.utils import safe_unicode
from five import grok
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from plone.dexterity.content import Container
from plone.keyring import django_random
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.supermodel import model
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.schema.vocabulary import getVocabularyRegistry

from wigo.statusapp.tool import IWigoTool
from wigo.statusapp.component import IComponent
from wigo.statusapp.servernode import IServerNode
from wigo.statusapp.incident import IIncident

from wigo.statusapp import MessageFactory as _


class IStatusApp(model.Schema, IImageScaleTraversable):
    """
    A collection of server status information
    """
    cluster = schema.TextLine(
        title=_(u"Cluster"),
        description=_(u"Automatically updated server cluster information"),
        required=False,
    )


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

    def prettify_status(self, status):
        vocabulary = self.status_vocabulary()
        term = vocabulary.getTerm(status)
        info = {}
        info['title'] = term.title
        info['value'] = term.value
        return info

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


class Components(grok.View):
    grok.context(IStatusApp)
    grok.require('cmf.ModifyPortalContent')
    grok.name('components')

    def update(self):
        self.has_components = len(self.components()) > 0

    def components(self):
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

    def prettify_status(self, status):
        vocabulary = self.status_vocabulary()
        term = vocabulary.getTerm(status)
        info = {}
        info['title'] = term.title
        info['value'] = term.value
        return info

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

    def contained_nodes(self, uuid):
        item = api.content.get(UID=uuid)
        nodes = item.restrictedTraverse('@@folderListing')()
        return nodes


class Incidents(grok.View):
    grok.context(IStatusApp)
    grok.require('cmf.ModifyPortalContent')
    grok.name('incidents')

    def update(self):
        self.has_incidents = len(self.incidents()) > 0

    def incidents(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IIncident.__identifier__,
                        sort_on='getObjPositionInParent')
        results = IContentListing(items)
        return results


class ServiceStatusAsJson(grok.View):
    """ Return service status json info

    This view is available to javascript frontend code and is meant to
    provide async status information on service nodes
    """
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('node-status-json')

    def update(self):
        self.host = self.request.get('host', None)
        self.service = self.request.get('service', 'http')

    def render(self):
        if self.host is not None:
            data = self.get_node_status()
            pretty = json.dumps(data, sort_keys=True)
            self.request.response.setHeader("Content-type", "application/json")
            return pretty

    def get_node_status(self):
        tool = getUtility(IWigoTool)
        status = tool.status(hostname=self.host, service=self.service)
        return status


class TransitionState(grok.View):
    grok.context(IContentish)
    grok.require('cmf.ModifyPortalContent')
    grok.name('transition-state')

    def render(self):
        context = aq_inner(self.context)
        uuid = self.request.get('uuid', '')
        state = api.content.get_state(obj=context)
        if state == 'published':
            api.content.transition(obj=context, transition='retract')
        else:
            api.content.transition(obj=context, transition='publish')
        came_from = api.content.get(UID=uuid)
        next_url = came_from.absolute_url()
        return self.request.response.redirect(next_url)


class BuildClusterInfo(grok.View):
    grok.context(IStatusApp)
    grok.require('cmf.ModifyPortalContent')
    grok.name('build-cluster-info')

    def get_components(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog(object_provides=IServerNode.__identifier__,
                        sort_on='getObjPositionInParent')
        return items

    def get_item_data(self, item):
        obj = item.getObject()
        hostname = getattr(obj, 'server')
        tool = getUtility(IWigoTool)
        info = {}
        info['id'] = obj.Title()
        info['uid'] = uuid_tool.uuid4()
        info['component'] = api.content.get_uuid(obj=obj)
        info['created'] = datetime.datetime.now(),
        info['hostname'] = hostname
        info['ip'] = getattr(obj, 'ip')
        info['server'] = getattr(obj, 'machine')
        try:
            data = tool.get(hostname=hostname)
            info['serverdetails'] = True
            info['id'] = data['server']
            info['hostname'] = data['servername']
            info['components'] = {
                'nginx': data['nginx'],
                'varnish': data['varnish'],
                'haproxy': data['haproxy']
            }
            info['sites'] = data['sites']
        except:
            info['serverdetails'] = False
        return info

    def get_items(self):
        results = self.get_components()
        items = []
        for r in results:
            item = self.get_item_data(r)
            items.append(item)
        return items

    def _process_request(self):
        api_url = self.request.get('ACTUAL_URL')
        data = {
            'url': api_url,
            'timestamp': int(time.time()),
        }
        if self.valid_token():
            items = self.get_items()
            data['count'] = len(items)
            data['items'] = items
        else:
            data['error'] = u"Access token invalid or missing from request"
        return data

    def render(self):
        start = time.time()
        data = self._process_request()
        end = time.time()
        data.update(dict(_runtime=end-start))
        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps(data)

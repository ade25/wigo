from five import grok
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory

from wigo.statusapp import MessageFactory as _


class IncidentTypeVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        TYPES = {
            _(u"Investigating"): 'investigating',
            _(u"Identified"): 'identified',
            _(u"Monitoring"): 'monitoring',
            _(u"Resolved"): 'resolved',
        }
        return SimpleVocabulary([SimpleTerm(value, title=title)
                                for title, value in TYPES.iteritems()])

grok.global_utility(IncidentTypeVocabulary,
                    name=u"wigo.statusapp.IncidentType")


class ComponentStatusVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        STATES = {
            _(u"Operational"): 'operational',
            _(u"Degraded Performance"): 'degradation',
            _(u"Partial Outage"): 'partial',
            _(u"Major Outage"): 'outage',
        }
        return SimpleVocabulary([SimpleTerm(value, title=title)
                                for title, value in STATES.iteritems()])

grok.global_utility(ComponentStatusVocabulary,
                    name=u"wigo.statusapp.ComponentStatus")

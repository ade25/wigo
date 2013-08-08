from zope.interface import directlyProvides
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory

from wigo.statusapp import MessageFactory as _


def IncidentTypeVocabulary(context):
    """ Vocabulary factory for incident types """
    TYPES = {
        _(u"investigating"): 'investigating',
        _(u"identified"): 'identified',
        _(u"monitoring"): 'monitoring',
        _(u"resolved"): 'resolved',
    }
    return SimpleVocabulary([SimpleTerm(value, title=title)
                             for title, value in TYPES.iteritems()])
directlyProvides(IncidentTypeVocabulary, IVocabularyFactory)


def ComponentStatusVocabulary(context):
    """ Vocabulary factory for incident types """
    STATES = {
        _(u"operational"): 'operational',
        _(u"performance degradation"): 'degradation',
        _(u"partial outage"): 'partial',
        _(u"outage"): 'outage',
    }
    return SimpleVocabulary([SimpleTerm(value, title=title)
                             for title, value in STATES.iteritems()])
directlyProvides(ComponentStatusVocabulary, IVocabularyFactory)

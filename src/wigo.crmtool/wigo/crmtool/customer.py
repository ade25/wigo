from five import grok

from zope import schema

from plone.dexterity.content import Container
from plone.directives import form
from plone.app.textfield import RichText
from plone.namedfile.interfaces import IImageScaleTraversable


from wigo.crmtool import MessageFactory as _


class ICustomer(form.Schema, IImageScaleTraversable):
    """
    A customer
    """
    cid = schema.TextLine(
        title=_(u"Customer ID"),
        description=_(u"Please enter a customer ID"),
        required=True,
    )
    street = schema.TextLine(
        title=_(u"Street"),
        required=True,
    )
    addressdetails = schema.TextLine(
        title=_(u"Addition to Address"),
        description=_(u"Optional supplement/details for the address"),
        required=False,
    )
    city = schema.TextLine(
        title=_(u"City"),
        required=True,
    )
    zipcode = schema.TextLine(
        title=_(u"ZIP"),
        required=True,
    )
    email = schema.TextLine(
        title=_(u"Email"),
        required=False,
    )
    phone = schema.TextLine(
        title=_(u"Phone"),
        required=False,
    )
    fax = schema.TextLine(
        title=_(u"Fax"),
        required=False,
    )
    twitter = schema.TextLine(
        title=_(u"Twitter Nickname"),
        description=_(u"Optional Twitter name like @example."),
        required=False,
    )
    facebook = schema.TextLine(
        title=_(u"Facebook URL"),
        description=_(u"Optional URL of a facebook fansite."),
        required=False,
    )
    text = RichText(
        title=_(u"Notes"),
        description=_(u"Add special information on this customer here"),
        required=False,
    )


class Customer(Container):
    grok.implements(ICustomer)


class View(grok.View):
    """ sample view class """

    grok.context(ICustomer)
    grok.require('zope2.View')
    grok.name('view')

    # Add view methods here

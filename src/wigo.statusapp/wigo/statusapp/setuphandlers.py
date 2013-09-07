from plone import api
from plone.app.controlpanel.security import ISecuritySchema


def setup_workspaces(portal):
    mp = api.portal.get_tool(name='portal_membership')
    # set type to custom member type
    mp.setMemberAreaType('wigo.workspaces.workspace')
    # set member folder name
    mp.setMembersFolderById('sqa')


def setup_security(portal):
    """ Add security controlpanel settings.
    """
    site = api.portal.get()
    #site security setup!
    security = ISecuritySchema(site)
    security.set_enable_user_folders(True)
    security.use_uuid_as_userid(True)


def setupVarious(context):
    if context.readDataFile('wigo.statusapp-various.txt') is None:
        return
    portal = api.portal.get()
    setup_workspaces(portal)
    # call update security
    setup_security(portal)

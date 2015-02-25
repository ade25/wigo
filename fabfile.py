import getpass
from fabric.api import task
from fabric.api import cd
from fabric.api import env
from fabric.api import run

from ade25.fabfiles import project
from ade25.fabfiles.server import controls

from slacker import Slacker
slack = Slacker('xoxp-2440800772-2440800774-2520374751-468e84')

env.use_ssh_config = True
env.forward_agent = True
env.port = '22222'
env.user = 'root'
env.hosts = ['wigo']
env.hostname = 'wigo'
env.webserver = '/opt/webserver/buildout.webserver'
env.code_root = '/opt/wigo/buildout.wigo'
env.local_root = '/Users/cb/dev/wigo/buildout.wigo'
env.sitename = 'wigo'
env.code_user = 'root'
env.prod_user = 'www'
# Uncomment and add your name here
env.actor = 'Christoph Boehner'


@task
def deploy(actor=None):
    """ Deploy current master to production server """
    opts = dict(
        sitename=env.get('sitename'),
        hostname=env.get('hostname'),
        actor=actor or env.get('actor') or getpass.getuser(),
    )
        project.site.update()
    project.site.restart()
        msg = '[%(hostname)s] *%(sitename)s* deployed by %(actor)s' % opts
    user = 'fabric'
    icon = ':shipit:'
    slack.chat.post_message('#general', msg, username=user, icon_emoji=icon)


@task
def deploy_full(actor=None):
    """ Deploy current master to production and run buildout """
    opts = dict(
        sitename=env.get('sitename'),
        hostname=env.get('hostname'),
        actor=actor or env.get('actor') or getpass.getuser(),
    )
    project.site.update()
    project.site.build()
        project.site.restart()
        msg = '[%(hostname)s] *%(sitename)s* deployed by %(actor)s' % opts
    user = 'fabric'
    icon = ':shipit:'
    slack.chat.post_message('#general', msg, username=user, icon_emoji=icon)


@task
def rebuild(actor=None):
    """ Deploy current master to production and run buildout """
    opts = dict(
        sitename=env.get('sitename'),
        hostname=env.get('hostname'),
        actor=actor or env.get('actor') or getpass.getuser(),
    )
    project.site.update()
    project.site.build_full()
        project.site.restart()
        msg = '[%(hostname)s] *%(sitename)s* rebuild by %(actor)s' % opts
    user = 'fabric'
    icon = ':shipit:'
    slack.chat.post_message('#general', msg, username=user, icon_emoji=icon)


@task
def get_data():
    """ Copy live database for local development """
    project.db.download_data()


@task
def ctl(*cmd):
    """Runs an arbitrary supervisorctl command."""
    with cd(env.webserver):
        run('nice bin/supervisorctl ' + ' '.join(cmd))

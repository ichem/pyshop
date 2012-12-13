import sys
from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy as ACLPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy as AuthPolicy

from .security import groupfinder

# used by pyramid
from .config import includeme
from .models import create_engine
from .helpers.i18n import locale_negotiator
from .helpers.authentication import RouteSwithchAuthPolicy

__version__ = '0.1'


def main(global_config, **settings):
    """Get a PyShop WSGI application configured with settings.
    """

    settings = dict(settings)

    if 'celery' in sys.argv[0]:
        # XXX celery must config sqlalchemy engine AFTER forkin consumer
        config = Configurator(settings=settings)
    else:
        # Scoping sessions for Pyramid ensure session are commit/rollback
        # after the template has been rendered
        create_engine(settings, scoped=True)

        authn_policy = RouteSwithchAuthPolicy(secret=settings['cookie_key'],
                                              callback=groupfinder)
        authz_policy = ACLPolicy()

        config = Configurator(settings=settings,
                              root_factory='pyshop.resources.RootFactory',
                              locale_negotiator=locale_negotiator,
                              authentication_policy=authn_policy,
                              authorization_policy=authz_policy)
    config.end()

    return config.make_wsgi_app()

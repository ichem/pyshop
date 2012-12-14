import os
import sys

from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import engine_from_config

from pyshop.helpers.sqla import create_engine, dispose_engine
from pyshop.models import (Base, DBSession,
                           Permission, Group, User,
                           )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def populate(engine):

    Base.metadata.create_all(engine)
    session = DBSession()
    user_perm = Permission(name=u'user_view')
    admin_perm = Permission(name=u'admin_view')
    download_perm = Permission(name=u'download_releasefile')
    upload_perm = Permission(name=u'upload_releasefile')
    session.add(user_perm)
    session.add(upload_perm)
    session.add(download_perm)
    session.add(admin_perm)

    user_group = Group(name=u'user')
    user_group.permissions.append(user_perm)
    user_group.permissions.append(download_perm)
    user_group.permissions.append(upload_perm)
    session.add(user_group)

    admin_group = Group(name=u'admin')
    admin_group.permissions.append(user_perm)
    admin_group.permissions.append(download_perm)
    admin_group.permissions.append(upload_perm)
    admin_group.permissions.append(admin_perm)
    session.add(admin_group)


    login = raw_input('administrator login [admin]:') or 'admin'
    password = raw_input('administrator password [changeme]:') or 'changeme'
    email = raw_input('administrator email [root@localhost]') or 'root@localhost'

    admin = User(login=unicode(login),
                 password=unicode(password),
                 email=unicode(email))
    admin.groups.append(user_group)
    admin.groups.append(admin_group)
    session.add(admin)

    session.commit()


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = create_engine('pyshop', settings, scoped=False)
    populate(engine)
    dispose_engine('pyshop')


if __name__ == '__main__':
    main()

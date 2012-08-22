#!/usr/bin/env python
"""
Fetches members of a steam group and adds them to a sourcemod admins database
"""

import sys
import urllib2
import xml.etree.ElementTree as ET

import config

# TODO: implement sqlite support
if config.db_type  == 'mysql':
    import MySQLdb
    db = MySQLdb.connect(user=config.db_user, passwd=config.db_pass,
                         db=config.db_database)
else:
    sys.exit('Unsupported db type')


def id64_to_str(id64):
    """Convert a steamid64 to a STEAM_X:Y:Z string"""
    y = id64 % 2
    z = ((id64 & 0xffffffff) - y)/ 2
    # 1 for csgo
    x = 1
    return 'STEAM_%d:%d:%d' % (x, y, z)


def gid_to_id64(gid):
    """Convert a steam group id to a steamid64"""
    return (0x0170000000000000 | gid)


def get_users(gid):
    """Returns a list of id64's"""
    url = 'http://steamcommunity.com/gid/%d/memberslistxml/?xml=1' % gid_to_id64(gid)
    xml = urllib2.urlopen(url).read()
    root = ET.fromstring(xml)
    users = []
    for id64 in root.iter('steamID64'):
        users.append(long(id64.text))
    return users


def add_admin(steamid, alias='', flags='', immunity=0):
    """Add an admin to the sql table

    If the admin exists fields are not updated.

    Returns the id for this admin

    """
    c = db.cursor()
    c.execute("""SELECT id FROM sm_admins WHERE authtype = 'steam' AND
              identity = %s""", steamid)
    result = c.fetchone()
    if result:
        (id,) = result
    else:
        c.execute("""INSERT INTO sm_admins (authtype, identity, flags,
                  name, immunity) VALUES ('steam', %s, %s, %s, %s)""",
                  (steamid, flags, alias, immunity))
        c.execute("""SELECT id FROM sm_admins WHERE authtype = 'steam' AND
                  identity = %s""", steamid)
        (id,) = c.fetchone()
    c.close()
    return id


def add_group(name, flags='', immunity=0):
    """Add an admin group to the sql table

    Returns the id for this group

    """
    c = db.cursor()
    c.execute("""SELECT id FROM sm_groups WHERE name = %s""", name)
    result = c.fetchone()
    if result:
        (id,) = result
    else:
        c.execute("""INSERT INTO sm_groups (name, flags, immunity)
                  VALUES (%s, %s, %s)""",
                  (name, flags, immunity))
        c.execute("""SELECT id FROM sm_groups WHERE name = %s""", name)
        (id,) = c.fetchone()
    c.close()
    return id


def add_admin_group(admin_id, group_id):
    c = db.cursor()
    c.execute("""SELECT * FROM sm_admins_groups WHERE admin_id = %s AND group_id = %s""",
              (admin_id, group_id))
    result = c.fetchone()
    if result:
        pass
    else:
        c.execute("""INSERT INTO sm_admins_groups (admin_id, group_id, inherit_order)
                  VALUES (%s, %s, 1)""", (admin_id, group_id))
    c.close()


for group in config.groups:
    group_id = add_group(group['name'], group['flags'], group['immunity'])
    users = get_users(group['id'])
    for user in users:
        admin_id = add_admin(id64_to_str(user))
        add_admin_group(admin_id, group_id)

db.commit()
db.close()

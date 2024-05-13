#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-


# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# If you have not received a copy of the GNU General Public License along
# with this program, see <https://www.gnu.org/licenses/>.


# part of mkp package "mikrotik"
# see ~/local/share/doc/check_mk/mikrotik for maintainer and information


#
#<<<mikrotik_vrrp>>>
#name IPTRANSIT_MYPROVIDER_IPv4        <- new session
#established True
#disabled False
#remote-address 5.6.7.8
#remote-as 12345
#name IPTRANSIT_MYPROVIDER_IPv6        <- new session


# import api
from .agent_based_api.v1 import (
    Metric,
    register,
    Result,
    State,
    Service,
)


# factory settings:
mikrotik_vrrp_factory_settings = {
}


# parse function
def parse_mikrotik_vrrp(string_table):

    # we'll return this later
    data = {}

    # loop thru
    for line in string_table:

        # a new seesion
        if line[0] == 'name':
            session       = line[1]
            data[session] = {}

        # all info for actual session
        data[session][line[0]] = ' '.join(line[1:])

    return data


# discovery function
def discover_mikrotik_vrrp(section):

    for vrrp in list(section):
        if section[vrrp]['disabled'] == 'false':
            yield Service( item=vrrp)


# check function
def check_mikrotik_vrrp(item, params, section):

    # initial
    mysummary    = []
    try:
        data=(section[item])
    except:
        yield Result(state=State.UNKNOWN, summary='not found')
        return

    # check state
    if data['running'] == 'true':
        try:
            if data['master'] == 'true':
                mysummary.append('%s on %s' % ('Master', data['interface']))
            else:
                mysummary.append('VRRP %s running on %s, but is not master(!!)' % (
                                  data['vrid'], 
                                  data['interface']))
        except:
                mysummary.append('VRRP %s running on %s, but does not seem to be master(!)' % (
                                  data['vrid'], 
                                  data['interface']))
    else:
        try:
            if data['backup'] == 'true':
                mysummary.append('%s on %s' % (
                                  'Currently Backup', 
                                  data['interface']))
            else:
                mysummary.append('VRRP %s not running on %s, but is not backup(!!)' % (
                                  data['vrid'], 
                                  data['interface']))
        except:
                mysummary.append('VRRP %s not running on %s, but does not seem to be backup(!)' % (
                                  data['vrid'], 
                                  data['interface']))

    # additional info
    mydetails = 'mac-address: %s' % data['mac-address']

    # disabled?
    if data['disabled'] != 'false':
        yield Result(state=State.WARN, summary='disabled: %s(!)' % data['disabled'])
        return

    # get worst state from markers
    mysummary = ', '.join(mysummary)
    mystate   = State.CRIT if '!!' in mysummary else State.WARN if '!' in mysummary else State.OK

    # this is the end, my friend
    yield Result(state=mystate, summary=mysummary, details=mydetails)
    return


# register parse function
register.agent_section(
    name                = "mikrotik_vrrp",
    parse_function      = parse_mikrotik_vrrp,
)


# register check
register.check_plugin(
    name                     = "mikrotik_vrrp",
    service_name             = "VRRP %s",
    discovery_function       = discover_mikrotik_vrrp,
    check_function           = check_mikrotik_vrrp,
    check_default_parameters = mikrotik_vrrp_factory_settings,
)

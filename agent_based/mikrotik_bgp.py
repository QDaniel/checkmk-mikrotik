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


# V6
#<<<mikrotik_bgp>>>
#name IPTRANSIT_MYPROVIDER_IPv4        <- new session
#established True
#remote-address 5.6.7.8
#remote-as 12345
#name IPTRANSIT_MYPROVIDER_IPv6        <- new session
#...

# V7
#<<<mikrotik_bgp>>>
#name IPTRANSIT_MYPROVIDER_IPv4        <- new session
#established True
#remote.address 5.6.7.8
#remote.as 12345
#name IPTRANSIT_MYPROVIDER_IPv6        <- new session
#...


# import api
from .agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
)

# factory settings:
mikrotik_bgp_factory_settings = {
}


# parse function
def parse_mikrotik_bgp(string_table):
    # we'll return this later
    data = {}
    entry = None
    idx = ''         
    # loop thru
    for line in string_table:
        # a new entry
        if line[0] == '.id':
            idx = line[1]

        if line[0] == 'name':
            entry           = line[1]
            data[entry]     = {}
            data[entry]['.id'] = idx
            data[entry]['remote.as'] = ''
            data[entry]['remote.address'] = ''
        if entry != None:
            # all info for actual session, rewrite some (v6'-' vs. v7'.', WTF)
            data[entry][line[0].replace('-', '.')] = ' '.join(line[1:])

    return data


# discovery function
def discover_mikrotik_bgp(section_mikrotik_bgp, section_mikrotik_bgp_sessions):

    for session in list(section_mikrotik_bgp):
        yield Service(item=session)


# check function
def check_mikrotik_bgp(item, params, section_mikrotik_bgp, section_mikrotik_bgp_sessions):

    # initial
    mysummary    = []
    try:
        data=(section_mikrotik_bgp[item])
    except:
        yield Result(state=State.UNKNOWN, summary='not found')
        return

    try:
        datasess=(section_mikrotik_bgp_sessions["%s-1" % item])
    except:
        pass



    # established?
    try:
        if datasess['established'] != 'true':
            yield Result(state=State.CRIT, summary='established: %s(!!)' % datasess['established'])
            return
    except:
        yield Result(state=State.CRIT, summary='no status info (!!)')
        return

    mysummary.append('Remote: AS %s, IP %s' % (datasess['remote.as'], datasess['remote.address']))

    # get worst state from markers
    mysummary = ', '.join(mysummary)
    mystate   = State.CRIT if '!!' in mysummary else State.WARN if '!' in mysummary else State.OK

    # this is the end, my friend
    yield Result(state=mystate, summary=mysummary)
    return


# register parse function
register.agent_section(
    name                = "mikrotik_bgp",
    parse_function      = parse_mikrotik_bgp,
)
register.agent_section(
    name                = "mikrotik_bgp_sessions",
    parse_function      = parse_mikrotik_bgp,
)


# register check
register.check_plugin(
    name                     = "mikrotik_bgp",
    sections                 = ["mikrotik_bgp", "mikrotik_bgp_sessions"],
    service_name             = "BGP %s",
    discovery_function       = discover_mikrotik_bgp,
    check_function           = check_mikrotik_bgp,
    check_default_parameters = mikrotik_bgp_factory_settings,
)

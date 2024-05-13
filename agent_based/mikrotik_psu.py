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


# RouterOS switch:
#<<<mikrotik_psu>>>
#psu2-state ok
#psu1-state ok

# RouterOS router:
#<<<mikrotik_psu>>>
#psu2-voltage 12.1
#psu1-voltage 12.1
#psu1-current 1.1
#psu2-current 3
#

# import api
from .agent_based_api.v1 import (
    Metric,
    register,
    Result,
    State,
    Service,
)


# factory settings:
mikrotik_psu_factory_settings = {
    "ok_states"    : ['ok']
}


# parse function
def parse_mikrotik_psu(string_table):

    # we'll return this later
    data = {}

    # current/voltage is handled in 'power' section of special agent.
    # If it is found here in 'psu', we can ignore.
    # So checking for "state" only is fine

    for line in string_table:
        
        # handle a psu related line
        if 'state' in line[0]:
            psu                = line[0].split('-')[0]
            data[psu]          = {}
            data[psu]['state'] = line[1]
            data[psu]['line']  = ' '.join(line)

    return data


# discovery function
def discover_mikrotik_psu(section):

    for psu in list(section):
        yield Service(item = psu)

# check function
def check_mikrotik_psu(item, params, section):

    data = section[item]
    state = data['state']

    if state in params['ok_states']:
        mysummary = 'State %s' % state
    else:
        mysummary = '%s(!!)' % data['line']

    # get worst state from markers
    mystate = State.CRIT if '!!' in mysummary else State.WARN if '!' in mysummary else State.OK

    # this is the end, my friend
    yield Result(state=mystate, summary=mysummary)
    return


# register parse function
register.agent_section(
    name                = "mikrotik_psu",
    parse_function      = parse_mikrotik_psu,
)


# register check
register.check_plugin(
    name                     = "mikrotik_psu",
    service_name             = "PSU %s",
    discovery_function       = discover_mikrotik_psu,
    check_function           = check_mikrotik_psu,
    check_default_parameters = mikrotik_psu_factory_settings,
)

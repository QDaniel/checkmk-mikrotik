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


#<<<mikrotik_ospf>>>
#router-id 56.129.214.198  <<- new neighbor
#address 56.129.214.146
#address sfp-sfpplus2.907
#state Full
#router-id 56.129.214.198  <<- new neighbor
#address 56.129.214.130
#address sfp-sfpplus3.906
#state Full
#router-id 56.129.214.193  <<- new neighbor


# import api
from .agent_based_api.v1 import (
    Metric,
    register,
    Result,
    State,
    Service,
)

# factory settings:
mikrotik_ospf_factory_settings = {
    "ok_states" : ['Full', 'TwoWay', '2-Way']
}

# parse function
def parse_mikrotik_ospf(string_table):

    # we'll return this later
    data = {}

    # loop thru
    for line in string_table:

        # a new neighbor?
        if line[0] == 'router-id':
            neighbor       = line[1]
            try:
                data[neighbor]
            except:
                data[neighbor] = {}
            continue

        # a new address
        if line[0] == 'address':
            address = line[1]
            continue

        # a state definition of current neighbor on current address
        if line[0] == 'state':
            data[neighbor][address] = ' '.join(line[1:])

    return data


# discovery function
def discover_mikrotik_ospf(section):

    for neighbor in list(section):
        yield Service( item=neighbor )


# check function
def check_mikrotik_ospf(item, params, section):

    # initial
    ospfstate = []
    mydetails = []
    try:
        data=(section[item])
    except:
        yield Result(state=State.UNKNOWN, summary='not found')
        return
    
    # state?
    try:
        for address in list(data):
            if data[address] in params['ok_states']:
                ospfstate.append('%s' % data[address])
                mydetails.append('%s: %s' % (address, data[address]))
                continue

            if data[address] == 'Down':
                ospfstate.append(' %s: Down(!!)' % address)
                continue

            # unknown state
            ospfstate.append('%s: %s(!)' % (address, data[address]))

    # OS 7 API lacks address info
    except:
        if data['state'] in params['ok_states']:
            ospfstate.append('%s' % data[address])
        else:
            ospfstate.append('%s(!!)' % data[address])


    # get worst state from markers
    mysummary = 'State%s: %s'% ( 
                     's' if len(data)>1 else '',
                     ' / '.join(list(dict.fromkeys(ospfstate))))

    mystate   = State.CRIT if '!!' in mysummary else State.WARN if '!' in mysummary else State.OK

    # this is the end, my friend
    try:
        yield Result(state=mystate, summary=mysummary, details='\n'.join(mydetails))
    except:
        yield Result(state=mystate, summary=mysummary)
    return


# register parse function
register.agent_section(
    name                = "mikrotik_ospf",
    parse_function      = parse_mikrotik_ospf,
)


# register check
register.check_plugin(
    name                     = "mikrotik_ospf",
    service_name             = "OSPF Neighbor %s",
    discovery_function       = discover_mikrotik_ospf,
    check_function           = check_mikrotik_ospf,
    check_default_parameters = mikrotik_ospf_factory_settings,
)

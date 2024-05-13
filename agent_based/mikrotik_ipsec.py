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


# active gateway:
#<<<mikrotik_ipsec>>>
#peer <name> <my ip> <peer ip>
#sa <peer ip> <my ip> mature 116840289 692937
#sa <my ip> <peer ip> mature 257940070 900964

# standby gateway:
#<<<mikrotik_ipsec>>>
#peer <name> <my ip> <peer ip>
#invip <my ip> vrrp4
#invip 10.200.5.254 vrrp5
#invip 10.200.3.254 vrrp3
#invip 10.200.6.1 vrrp6


# import api
from .agent_based_api.v1 import (
    get_rate,
    get_value_store,
    Metric,
    register,
    render,
    Result,
    State,
    Service,
)

import time


# factory settings:
mikrotik_ipsec_factory_settings = {
    "ok_states"    : ['dying', 'mature']
}


# parse function
def parse_mikrotik_ipsec(string_table):

    # we'll return this later
    data = {}


    for line in string_table:


        if line[0] == 'peer':
            dstaddr       = line[3]
            data[dstaddr] = {}

            data[dstaddr]['myaddr']    = line[2]
            data[dstaddr]['peer']      = line[1]
            data[dstaddr]['sa_states'] = []

            for what in ['sacount', 'if_in_bps', 'if_out_bps']:
                data[dstaddr][what] = 0

            continue

        # active gateway
        if line[0] == 'sa':


            # bandwidth info of current SA
            if line[1] in list(data):
                dstaddr = line[1]
                what    = 'if_out_bps'

            elif line[2] in list(data):
                dstaddr = line[2]
                what    = 'if_in_bps'

            else:
                continue # should never happen, this would be a SA without peer

            # the current information
            data[dstaddr][what]      += int(line[4])
            data[dstaddr]['sacount'] += 1

            data[dstaddr]['sa_states'].append(line[3])

            continue

        # standby gateway
        if line[0] == 'invip':

            try:
                for dstaddr in list(data):
                    if data[dstaddr]['myaddr'] == line[1]:
                        data[dstaddr]['if'] = line[2]
            except:
                continue


    return data


# discovery function
def discover_mikrotik_ipsec(section):

    for dstaddr in list(section):
        yield Service(item = section[dstaddr]['peer'])


# check function
def check_mikrotik_ipsec(item, params, section):

    # initial
    try:
        for dstaddr in list(section):
            if section[dstaddr]['peer'] == item:
                data = section[dstaddr]
                break
    except:
        yield Result(state=State.UNKNOWN, summary='not found')
        return

    mysummary   = []
    value_store = get_value_store()
    now         = time.time()

    # metrics
    bytes_i_rate = get_rate(value_store, 
                            "mikrotik_ipsec.%s.bytes_i" % item, 
                            now,
                            data['if_in_bps']) 
    bytes_o_rate = get_rate(value_store, 
                            "mikrotik_ipsec.%s.bytes_o" % item, 
                            now, 
                            data['if_out_bps'])
    yield Metric('if_in_bps',  int(bytes_i_rate*8))
    yield Metric('if_out_bps', int(bytes_o_rate*8))

    # active
    if data['sacount'] > 0:
        mysummary.append('%s...%s' % (data['myaddr'], dstaddr))
        mydetails = 'current Security Associations: %s' % data['sacount']

        # check state of SA
        for sa_state in set(data['sa_states']):
            if sa_state not in params['ok_states']:
                mysummary.append('bad SA state found: %s(!!)' % sa_state)

        # show bandwidth info only on OK state to keep summary small
        if '!' not in ' '.join(mysummary):
            mysummary.append('in: %s'  % render.networkbandwidth(bytes_i_rate))
            mysummary.append('out: %s' % render.networkbandwidth(bytes_o_rate))

    # standby
    else:
        try:
            mysummary.append('Currently Standby')
            mydetails = '%s not active on %s' % (data['myaddr'], data['if'])
        except:
            mysummary.append('IPsec in unknown state(!!)')
            mydetails = str(data)


    # get worst state from markers
    mysummary = ', '.join(mysummary)
    mystate   = State.CRIT if '!!' in mysummary else State.WARN if '!' in mysummary else State.OK


    # this is the end, my friend
    yield Result(state=mystate, summary=mysummary, details=mydetails)
    return


# register parse function
register.agent_section(
    name                = "mikrotik_ipsec",
    parse_function      = parse_mikrotik_ipsec,
)


# register check
register.check_plugin(
    name                     = "mikrotik_ipsec",
    service_name             = "IPsec %s",
    discovery_function       = discover_mikrotik_ipsec,
    check_function           = check_mikrotik_ipsec,
    check_ruleset_name       = "mikrotik_ipsec",
    check_default_parameters = mikrotik_ipsec_factory_settings,
)

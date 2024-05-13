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


#<<<mikrotik_interfaces>>>
#.id *18
#name wgUSERS
#type wg
#mtu 1400
#actual-mtu 1400
#last-link-up-time 2024-04-12 23:27:15
#link-downs 0
#rx-byte 148982960
#tx-byte 1121220184
#rx-packet 508518
#tx-packet 984710
#rx-drop 0
#tx-drop 3879
#tx-queue-drop 0
#rx-error 10
#tx-error 660444
#fp-rx-byte 0
#fp-tx-byte 0
#fp-rx-packet 0
#fp-tx-packet 0
#running true
#disabled false



# - comment is always first, followed by k/v of this rule
#   - comment becomes item
#   - can be shortend by keyword "checkmk: "
#   - above examples:
#     "comment anti-spoofing - permit customer prefixes to outside only"
#        -> "Firewall Filter comment anti-spoofing - permit customer prefixes to outside only"
#     "comment blacklist rules based on address list (checkmk: blacklist)"
#        -> "Firewall Filter blacklist"
# - 'None' means no info from api for that key
# - 'comment None' will not inventarize


#from .agent_based_api.v1 import *
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
from .utils import interfaces


# parse function
def parse_mikrotik_interfaces(string_table):

    # we'll return this later
    if_table = []
    data  = {}
    iface = ''
    idx=''
    for line in string_table:
        # a new interface
        if line[0] == '.id':
            idx=line[1]
            continue

        if line[0] == 'name':
            iface       = line[1]
            data[iface] = {}
            data[iface]['.id'] = idx
            data[iface]['idx'] = int(idx.replace('*',''), 16)
            data[iface]['mac-address'] = None

        # all info for actual session, rewrite some (v6'-' vs. v7'.', WTF)
        if iface != '':
            data[iface][line[0]] = ' '.join(line[1:])

    for nic in list(data):
        if_table.append( interfaces.InterfaceWithCounters(
            interfaces.Attributes(
                index=data[nic]['idx'],
                descr=data[nic]['name'],
                alias=data[nic]['name'],
                type="24" if data[nic]['name'] == "lo" else "6",
                speed=1000000000,
                oper_status="1" if data[nic]['disabled'] == "false" else "2",
                phys_address=interfaces.mac_address_from_hexstring(data[nic]['mac-address'])
            ),
            interfaces.Counters(
                in_octets  = int(data[nic]['rx-byte']),
                in_ucast=int(data[nic]['rx-packet']),
                in_mcast=0,
                in_bcast=0,
                in_disc=int(data[nic]['rx-drop']),
                in_err=int(data[nic]['rx-error']),
                out_octets=int(data[nic]['tx-byte']),
                out_ucast=int(data[nic]['tx-packet']),
                out_mcast=0,
                out_bcast=0,
                out_disc=int(data[nic]['tx-drop']),
                out_err=int(data[nic]['tx-error']),
            ),
        ))
    return if_table, data

# discovery function
def discover_mikrotik_interfaces(params, section):
    yield from interfaces.discover_interfaces(
        params,
        section[0],
    )

# check function
def check_mikrotik_interfaces(item, params, section):
    # initial
    try:
        dictval = section[1].values()
        data = next(x for x in dictval if x['name'] == item or (item.isdigit() and x['idx'] == int(item)))
    except:
        yield from interfaces.check_multiple_interfaces(
            item,
            params,
            section[0],
        )
        return
    
 
    value_store = get_value_store()
    now         = time.time()

    # metrics
    yield Metric('if_in_bps', get_rate(value_store, "mikrotik_interface.%s.in" % item, now, int(data['rx-byte'])) *8)
    yield Metric('if_out_bps', get_rate(value_store, "mikrotik_interface.%s.out" % item, now, int(data['tx-byte'])) *8)
    yield from interfaces.check_multiple_interfaces(
        item,
        params,
        section[0],
    )
    return

# register parse function
register.agent_section(
    name                = "mikrotik_interfaces",
    parse_function      = parse_mikrotik_interfaces,
)


# register check
register.check_plugin(
    name                     = "mikrotik_interfaces",
    service_name             = "Interface %s",
    discovery_ruleset_name="inventory_if_rules",
    discovery_ruleset_type=register.RuleSetType.ALL,
    discovery_default_parameters=dict(interfaces.DISCOVERY_DEFAULT_PARAMETERS),
    discovery_function       = discover_mikrotik_interfaces,
    check_function           = check_mikrotik_interfaces,
    check_default_parameters = interfaces.CHECK_DEFAULT_PARAMETERS,
    check_ruleset_name="interfaces",

)

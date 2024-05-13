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


#<<<mikrotik_firewall>>>
#comment anti-spoofing - permit customer prefixes to outside only
#.id *22
#chain forward
#bytes 3865890417
#packets 4148355
#disabled None
#comment None
#.id *23
#chain forward
#bytes 46066785198
#packets 156794722
#disabled None
#comment blacklist rules based on address list (checkmk: blacklist)
#.id *19
#chain deny_src
#bytes 1092346897
#packets 10988418
#disabled None

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


# factory settings:
mikrotik_firewall_factory_settings = {
}


# parse function
def parse_mikrotik_firewall(string_table):

    # we'll return this later
    data = {}


    for line in string_table:
        if line[0] == 'comment':

            # use rule comment for item
            # no other way to identify rule: id changes with position
            # :o(
            rule = ' '.join(line[1:])

            # use a short name if configured
            if 'checkmk:' in rule:
                rule = rule.split('checkmk: ')[1].strip(')')

            data[rule] = {}
            data[rule]['comment'] = ' '.join(line[1:])

            continue

        if line[0] == 'bytes':
            data[rule]['if_total_octets'] = int(line[1])
            continue

        if line[0] in ['chain', 'disabled']:
            data[rule][line[0]] = ' '.join(line[1:])
            continue

    return data


# discovery function
def discover_mikrotik_firewall(section):

    for rule in list(section):
        if rule != 'None' and section[rule]['disabled'] == 'None':
            yield Service(item = rule)


# check function
def check_mikrotik_firewall(item, params, section):

    # initial
    try:
        data = section[item]
    except:
        yield Result(state=State.UNKNOWN, summary='not found')
        return

    mysummary   = []
    value_store = get_value_store()
    now         = time.time()

    # a now disabled rule was enabled on discovery, so we drop some WARN
    if data['disabled'] == 'true':
        mysummary.append('disabled: %s(!)' % data['disabled'])

    mysummary.append('Chain: %s' % data['chain'])
    mydetails = 'Comment: \"%s\"' % data['comment']

    # metrics
    bytes_rate = get_rate(value_store, "mikrotik_firewall.%s.bytes" % 
                                                          item, now, data['if_total_octets'])
    yield Metric('if_total_bps', bytes_rate*8)
    mysummary.append('%s' % render.networkbandwidth(bytes_rate))

    # get worst state from markers
    mysummary = ', '.join(mysummary)
    mystate   = State.CRIT if '!!' in mysummary else State.WARN if '!' in mysummary else State.OK

    # this is the end, my friend
    yield Result(state=mystate, summary=mysummary, details=mydetails)
    return


# register parse function
register.agent_section(
    name                = "mikrotik_firewall",
    parse_function      = parse_mikrotik_firewall,
)


# register check
register.check_plugin(
    name                     = "mikrotik_firewall",
    service_name             = "Firewall Filter %s",
    discovery_function       = discover_mikrotik_firewall,
    check_function           = check_mikrotik_firewall,
    check_default_parameters = mikrotik_firewall_factory_settings,
)

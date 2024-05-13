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


#<<<mikrotik_fan>>>
#fan1-speed 4062
#use-fan main
#fan-mode auto
#fan2-speed 4062
#active-fan main


# import api
from .agent_based_api.v1 import (
    Metric,
    register,
    Result,
    State,
    Service,
)


# factory settings:
mikrotik_fan_factory_settings = {
    "lower"          : (2000, 1000),
    "output_metrics" : True
}


# parse function
def parse_mikrotik_fan(string_table):

    # we'll return this later
    data = {}

    # loop thru
    for line in string_table:
        
        # handle a related line
        if 'speed' in line[0]:

            fan                = line[0].split('-')[0]
            data[fan]          = {}
            data[fan]['speed'] = int(line[1])

    return data


# discovery function
def discover_mikrotik_fan(section):

    # skip fans with zero speed on discovery
    # they are more likely absent than defective
    for key in list(section):
        if section[key]['speed'] > 0:
            yield Service( item=key )


# check function
def check_mikrotik_fan(item, params, section):

    # initial
    w, c = params['lower']
    s    = section[item]['speed']
    
    # check
    marker = '(!!) (below %s)' % c if s < c else '(!) (below %s)' % w if s < w else ''

    # be verbose
    mysummary = 'Speed: %s RPM%s' % (s, marker)

    # metrics
    if params['output_metrics']:
        yield Metric('fan', s, levels=(w, c))

    # get worst state from markers
    mystate = State.CRIT if '!!' in mysummary else State.WARN if '!' in mysummary else State.OK

    # this is the end, my friend
    yield Result(state=mystate, summary=mysummary)
    return


# register parse function
register.agent_section(
    name                = "mikrotik_fan",
    parse_function      = parse_mikrotik_fan,
)


# register check
register.check_plugin(
    name                     = "mikrotik_fan",
    service_name             = "FAN %s",
    discovery_function       = discover_mikrotik_fan,
    check_function           = check_mikrotik_fan,
    check_ruleset_name       = "mikrotik_fan",
    check_default_parameters = mikrotik_fan_factory_settings,
)

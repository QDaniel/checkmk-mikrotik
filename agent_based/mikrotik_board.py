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


#<<<mikrotik_board>>>
#uptime 16w4d5h42m51s
#version 7.11.2 (stable)
#build-time Aug/31/2023 13:55:47
#factory-software 7.6
#free-memory 3971874816
#total-memory 4227858432
#cpu ARM64
#cpu-count 4
#cpu-load 0
#free-hdd-space 110362624
#total-hdd-space 135266304
#write-sect-since-reboot 404211
#write-sect-total 421157
#bad-blocks 0
#architecture-name arm64
#board-name CCR2004-16G-2S+
#platform MikroTik



# import api
from .agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
)

from distutils.version import StrictVersion


# factory settings:
mikrotik_board_factory_settings = {
    "min_version"    : '0.0'
}


# parse function
def parse_mikrotik_board(string_table):

    # we'll return this later
    data = {}

    # loop thru
    for line in string_table:

        # only relevant info
        if line[0] in ['board-name', 'version']:
                data[line[0]] = ' '.join(line[1:])

    return data


# discovery function
def discover_mikrotik_board(section):

    if section['version']:
        yield Service()


# check function
def check_mikrotik_board(params, section):

    # initial
    mysummary = []
    minv      = params['min_version']

    # loop thru

    for what in list(section):

        # if version checking is requested ...
        if what == 'version' and params['min_version'] != '0.0':
            
            # ... then WARN if less the minimum required, else mark OK
            if StrictVersion(section[what].split(' ')[0]) >= StrictVersion(params['min_version']):
                mysummary.append('%s: %s(.)' % (
                                    what, 
                                    section[what]))
            else:
                mysummary.append('%s: %s(!) (below %s)' % (
                                    what, 
                                    section[what], 
                                    params['min_version']))
        # any info
        else:
            mysummary.append('%s: %s' % (what, section[what]))


    # get worst state from markers (no crit in this check)
    mysummary = ', '.join(mysummary)
    mystate   = State.WARN if '!' in mysummary else State.OK

    # this is the end, my friend
    yield Result(state=mystate, summary=mysummary)
    return


# register parse function
register.agent_section(
    name                = "mikrotik_board",
    parse_function      = parse_mikrotik_board,
)


# register check
register.check_plugin(
    name                     = "mikrotik_board",
    service_name             = "RouterOS Info",
    discovery_function       = discover_mikrotik_board,
    check_function           = check_mikrotik_board,
    check_ruleset_name       = "mikrotik_board",
    check_default_parameters = mikrotik_board_factory_settings,
)

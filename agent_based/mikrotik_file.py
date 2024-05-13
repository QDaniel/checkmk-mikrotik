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


#<<<mikrotik_file>>>
#name serial.txt        <- new file
#.id *D3EF6
#type .txt file
#creation-time jan/19/2021 07:32:38
#name bl.txt            <- new file


from .agent_based_api.v1 import (
    register,
    render,
    Result,
    State,
    Service,
)

import time


# factory settings:
mikrotik_file_factory_settings = {
    "file_age"      : ( 90000, 176400 ),  # 25h/49h
    "pattern"       : '' # as returned by API, empty for autodetection
}


# parse function
def parse_mikrotik_file(string_table):

    # we'll return this later
    data = {}

    # loop thru
    for line in string_table:

        if line[0] == 'name':
            file       = line[1]
            data[file] = {}

        data[file][line[0]] = ' '.join(line[1:])

    if 'autosupout.rif' not in data:
        data['autosupout.rif']         = {}
        data['autosupout.rif']['type'] = 'file'

    return data


# discovery function
def discover_mikrotik_file(section):

    for file in list(section):
        if section[file]['type'] != 'directory':
            yield Service(item = file)

# check function
def check_mikrotik_file(item, params, section):

    # initial
    mysummary = []

    try:
        data = section[item]

    except:
        yield Result(state=State.UNKNOWN, summary='not found')
        return

    # watchdog
    if item == 'autosupout.rif':
        if 'creation-time' not in data:
            yield Result(state=State.OK, summary='Watchdog file not found(.)')
            return
        else:
            mysummary.append('Watchdog file found(!!)')

    # get epoch from time info and check age
    try:
        creation_time = data['creation-time']

        if params['pattern'] == '':
            if '/' in creation_time:
                pattern = '%b/%d/%Y %H:%M:%S'
            else:
                pattern = '%Y-%m-%d %H:%M:%S'
        else:
            pattern = params['pattern']


        age           = int(time.time()-time.mktime(time.strptime(creation_time, pattern)))
        hr_age        = render.timespan(age)

        warn, crit    = params['file_age']

        if age > crit:
             hr_age  += '(!!) (older than %s)' % render.timespan(crit)
        elif age > warn:
             hr_age  +=  '(!) (older than %s)' % render.timespan(warn)

    except:
        hr_age        = 'cannot calculate(!)'

    # output
    mysummary.append('Created: %s (%s ago)' % (creation_time.capitalize(), hr_age))
    mysummary=', '.join(mysummary)


    # get worst state from markers
    mystate   = State.CRIT if '!!' in mysummary else State.WARN if '!' in mysummary else State.OK

    # this is the end, my friend
    yield Result(state=mystate, summary=mysummary)
    return


# register parse function
register.agent_section(
    name                = "mikrotik_file",
    parse_function      = parse_mikrotik_file,
)


# register check
register.check_plugin(
    name                     = "mikrotik_file",
    service_name             = "File %s",
    discovery_function       = discover_mikrotik_file,
    check_function           = check_mikrotik_file,
    check_ruleset_name       = "mikrotik_file",
    check_default_parameters = mikrotik_file_factory_settings,
)

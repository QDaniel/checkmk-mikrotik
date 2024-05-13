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


#<<<mikrotik_power>>>
#power-consumption 45.9
#psu1-current 0.2
#psu2-current 3.6
#psu1-voltage 12.1
#psu2-voltage 12.1


# import api
from .agent_based_api.v1 import (
    Metric,
    register,
    Result,
    State,
    Service,
)


# factory settings:
mikrotik_power_factory_settings = {
    "crit_voltage"    : 10
}


# parse function
def parse_mikrotik_power(string_table):

    # we'll return this later
    data         = {}
    data['psus'] = {}

    # loop thru
    for line in string_table:

        # one psu:
        if line[0] in ['current', 'voltage']:
             line[0] = 'psu0-%s' % line[0]

        # skip non interesting line
        if 'psu' not in line[0]:
            continue

        temp   = line[0].split('-')
        psu    = temp[0].upper()
        metric = temp[1]
        value  = float(line[1])

        # detect mA vs. A
        if metric == 'current' and value > 100:
            value = value / 1000

        # create new psu dict if missing
        if psu not in data['psus'].keys():
            data['psus'][psu] = {}

        # the values
        data['psus'][psu][metric] = value

    # calc power-consumption
    data['power-consumption'] = 0
    for psu in data['psus'].keys():
       data['power-consumption'] += data['psus'][psu]['current'] * data['psus'][psu]['voltage']

    return data


# discovery function
def discover_mikrotik_power(section):

    yield Service(parameters={'psu_count':len(section['psus'])})


# check function
def check_mikrotik_power(params, section):

    # initial
    mysummary    = []
    mydetails    = []
    psu_exp      = params['psu_count']
    crit_voltage = params['crit_voltage']
    psu_count    = len(section['psus'])
    current      = 0.0
    voltage      = 0.0

    # handle missing or attached psu    
    if psu_count != psu_exp and psu_exp != 0:
        mysummary.append('%d PSU(!) (expected %s)' % (psu_count, psu_exp))
    else:
        mysummary.append('%d PSU' % (psu_count))

    # loop thru PSUs
    for psu in section['psus'].keys():

        # check undervoltage (might indicate power outage)
        if section['psus'][psu]['voltage'] < params['crit_voltage']:
            mysummary.append('%s low voltage(!!))' % psu)

        # be kind in details
        mydetails.append('%s: %sV / %sA' % (
                          psu,
                          section['psus'][psu]['voltage'],
                          section['psus'][psu]['current']))

        # get the overalls
        current += section['psus'][psu]['current']
        voltage  = max(voltage, section['psus'][psu]['voltage'])
        
    # power
    if section['power-consumption'] > 0:
        mysummary.append('Power: %s W' % round(section['power-consumption']))
        yield Metric('power', section['power-consumption'])
    else:
        mysummary.append('Voltage: %s V' % round(voltage, 2))

    # metrics
    if current > 0:
        yield Metric('current', current)
    if voltage > 0:
        yield Metric('voltage', voltage)

    # get worst state from markers
    mysummary = ', '.join(mysummary)
    mystate   = State.CRIT if '!!' in mysummary else State.WARN if '!' in mysummary else State.OK

    # this is the end, my friend
    try:
        mydetails = ', '.join(mydetails)
        yield Result(state=mystate, summary=mysummary, details=mydetails)
    except:
        yield Result(state=mystate, summary=mysummary)
    return


# register parse function
register.agent_section(
    name                = "mikrotik_power",
    parse_function      = parse_mikrotik_power,
)


# register check
register.check_plugin(
    name                     = "mikrotik_power",
    service_name             = "Power Usage",
    discovery_function       = discover_mikrotik_power,
    check_function           = check_mikrotik_power,
    check_default_parameters = mikrotik_power_factory_settings,
)

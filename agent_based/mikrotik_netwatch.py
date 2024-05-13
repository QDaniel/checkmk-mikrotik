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


#<<<mikrotik_netwatch>>>
#.id *1
#host 4.2.2.2
#type icmp
#src-address
#interval 10s
#timeout 5s
#start-delay 0ms
#test-script
#packet-interval 50ms
#packet-count 10
#thr-max 1s
#thr-avg 400ms
#http-codes
#status up
#since 2024-05-11 09:08:27
#done-tests 23689
#failed-tests 650
#sent-count 10
#response-count 10
#loss-count 0
#loss-percent 0
#rtt-avg 13ms10us
#rtt-min 11ms350us
#rtt-max 16ms596us
#rtt-jitter 5ms246us
#rtt-stdev 1ms746us
#disabled false
#.id *2
#name 10.33.6.78
#host 10.33.6.78
#type icmp
#src-address 10.33.6.77
#up-script
#down-script
#test-script
#http-codes
#status up
#since 2024-05-10 17:10:20
#done-tests 23664
#failed-tests 188
#sent-count 10
#response-count 10
#loss-count 0
#loss-percent 0
#rtt-avg 27ms21us
#rtt-min 26ms803us
#rtt-max 27ms573us
#rtt-jitter 770us
#rtt-stdev 313us
#disabled false
#<<<>>>

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
    check_levels,
)

import time, re
from datetime import timedelta


# factory settings:
mikrotik_netwatch_factory_settings = {
}


# parse function
def parse_mikrotik_netwatch(string_table):
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
        if entry != None:
            if line[0] in ['rtt-avg', 'rtt-min', 'rtt-max', 'rtt-jitter', 'rtt-stdev']:
                data[entry][line[0]] = parse_mkt_timedelta(line[1])
            elif line[0] in ['loss-count', 'sent-count', 'done-tests', 'failed-tests']:
                data[entry][line[0]] = int(line[1])
            else:
                data[entry][line[0]] = ' '.join(line[1:])
    return data


# discovery function
def discover_mikrotik_netwatch(section):
    for iface in list(section):
        yield Service(item = iface)


# check function
def check_mikrotik_netwatch(item, params, section):

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
    if data['status'] == 'down':
        mysummary.append('status: %s(!!)' % data['status'])
 
    #yield Metric('pl',  data['loss-percent']) 
    mysummary.append('Lost: %s%%' % data['loss-percent'])

    yield Metric('rta',  data['rtt-avg']) 
    mysummary.append('Avg: %s' % render.timespan(data['rtt-avg']))

    yield Metric('rtmin',  data['rtt-min'])
    mysummary.append('Min: %s' % render.timespan(data['rtt-min']))

    yield Metric('rtmax',  data['rtt-max'])
    mysummary.append('Max: %s' % render.timespan(data['rtt-max']))

    # get worst state from markers
    mysummary = ', '.join(mysummary)
    mystate   = State.CRIT if '!!' in mysummary else State.WARN if '!' in mysummary else State.OK

    yield from check_levels( float(data['loss-percent']),
        levels_upper = (10.0, 50.0),
        metric_name = "pl",
        label = "Lost Packets",
        boundaries = (0.0, 100.0),
        notice_only = True,
    )
    # this is the end, my friend
    yield Result(state=mystate, summary=mysummary)
    return

def parse_mkt_timedelta(time):
	
    time_dict = re.match(r'((?P<weeks>\d+)w)?((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?((?P<milliseconds>\d+)j)?((?P<microseconds>\d+)us)?', time.replace("ms", "j")).groupdict()
    delta = timedelta(**{key: int(value) for key, value in time_dict.items() if value}).total_seconds() 
    return delta

# register parse function
register.agent_section(
    name                = "mikrotik_netwatch",
    parse_function      = parse_mikrotik_netwatch,
)


# register check
register.check_plugin(
    name                     = "mikrotik_netwatch",
    service_name             = "Netwatch %s",
    discovery_function       = discover_mikrotik_netwatch,
    check_function           = check_mikrotik_netwatch,
    check_default_parameters = mikrotik_netwatch_factory_settings,
)

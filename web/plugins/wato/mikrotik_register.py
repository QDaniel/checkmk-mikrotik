#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2014             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# this file is part of mkp package "mikrotik"
# see package description for details
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

#
from cmk.gui.plugins.wato import (
    HostRulespec,
    IndividualOrStoredPassword,
    monitoring_macro_help,
    RulespecGroup,
    rulespec_group_registry,
    rulespec_registry,
)

# thx @aeckstein
from cmk.gui.valuespec import (
    Dictionary,
    TextInput,
    DropdownChoice,
    Integer,
    ListChoice,
)

#
from cmk.gui.plugins.wato.datasource_programs import RulespecGroupDatasourceProgramsHardware

#
def _valuespec_special_agent_mikrotik():
    return Dictionary(
        title = _("MikroTik RouterOS"),
        help  = _("This rule activates an agent that collects information from "
                 "MikroTik RouterOS API. Surprisingly this includes some switches."),

        optional_keys = [],

        elements = [
            ( "user",
                TextInput(
                    title       = _("Username"),
                    allow_empty = False,
                )
            ),
            ( "password",
                Password(
                    title       = _("Password"),
                    allow_empty = False,
                )
            ),
            ( "nossl",
               DropdownChoice(
                   title   = _("Type of query"),
                   choices = [
                       ( False, _("Use SSL (Default)" ) ),
                       ( True,  _("Do not use SSL to connect to API") ),
                   ],
                   default_value = False,
               )
            ),
            ( "connect",
               Integer(
                    title         = _("TCP port number"),
                    help          = _("Port number for connection to API. Usually 8729 (SSL) "
                                      "or 8728 (no SSL)"),
                    default_value = 8729,
                    minvalue      = 1,
                    maxvalue      = 65535,
               )
            ),
            ( "infos",
                Transform(
                    ListChoice(
                        choices = [
                            ( "bgp",      _("BGP Sessions")),
                            ( "ospf",     _("OSPF Neighbors")),
                            ( "vrrp",     _("VRRP Info")),
                            ( "health",   _("RouterOS Health")),
                            ( "board",    _("RouterOS Board Info")),
                            ( "ipsec",    _("IPsec")),
                            ( "firewall", _("Firewall Rules")),
                            ( "file",     _("Local File Age")),
                            ( "interfaces", _("Interfaces")),
                            ( "netwatch", _("Netwatch")),
                        ],
                        default_value = [ "health", "board" ],
                        allow_empty   = False,
                     ),
                title = _("Retrieve information about..."),
                )
            ),
        ],
    )


#
rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsHardware,
        name="special_agents:mikrotik",
        valuespec=_valuespec_special_agent_mikrotik,
    ))

#!/usr/bin/env python3
#
# part of mkp package "mikrotik"
# see package description for details
#

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Alternative,
    Integer,
    ListOfStrings,
    Percentage,
    Tuple,
)

from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithItem,
    CheckParameterRulespecWithoutItem,
    rulespec_registry,
    RulespecGroupCheckParametersStorage,
)

def _item_spec_mikrotik_fan():
    return TextAscii(title=_("MikroTik Fan"))


def _parameter_valuespec_mikrotik_fan():
    return Dictionary(
        title    = _("MikroTik Fan"),
        help     = _("Activate special agent mikrotik to use this."),
        elements = [
            ("output_metrics",
                DropdownChoice(
                    title   = _("Performance Graph"),
                    help     = _("If set to <b>disable</b> on existing fans "
                                 "delete RRD files to completely remove graphs."),
                    choices = [
                        ( True,  _("enable (default)") ),
                        ( False, _("disable" ) ),
                    ],
                    default_value = True,
                )
            ),
            ("lower",
                Tuple(
                    title    = _("Lower levels"),
                    help     = _("Lower levels for the fan speed"),
                    elements = [
                        Integer(
                            title         = _("Warning if below"),
                            unit          = _("rpm"),
                            default_value = 2000
                        ),
                        Integer(
                            title         = _("Critical if below"),
                            unit          = _("rpm"),
                            default_value = 1000
                        )
                    ]
                )
            ),
        ],
    )

rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="mikrotik_fan",
        group=RulespecGroupCheckParametersApplications,
        item_spec=_item_spec_mikrotik_fan,
        parameter_valuespec=_parameter_valuespec_mikrotik_fan,
        title=lambda: _("MikroTik Fan"),
    )
)



def _parameter_valuespec_mikrotik_board():
    return Dictionary(
        title    = _("MikroTik RouterOS"),
        help     = _("Activate special agent mikrotik to use this."),
        elements = [
            ("min_version",
                TextAscii(
                    title         = _("Minimum Version"),
                    help          = _("If set check will go WARN if installed version is lower"),
                    regex         = "^[0-9]*\.[0-9]",
                    regex_error   = _("Enter a correct version number (e.g. "
                                      "<b><tt>Major.Minor</tt></b> or "
                                      "<b><tt>Major.Minor.Patch</tt></b>)"),
                    default_value = '0.0'

                )
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="mikrotik_board",
        group=RulespecGroupCheckParametersApplications,
        parameter_valuespec=_parameter_valuespec_mikrotik_board,
        title=lambda: _("MikroTik RouterOS"),
    )
)



def _item_spec_mikrotik_file():
    return TextAscii(title=_("MikroTik File"))

def _parameter_valuespec_mikrotik_file():
    return Dictionary(
        title    = _("MikroTik File"),
        help     = _("Activate special agent mikrotik to use this."),
        elements = [
            ("file_age",
                Tuple(
                 title = _("Age of File Creation"),
                 elements = [
                     Age(title = _("Warning if older than"), default_value = 90000),
                     Age(title = _("Critical if older than"), default_value = 176400)
                     ]
                 )
            ),
            ( "pattern",
                TextAscii(
                    title = _("Time Pattern (see inline help for examples)"),
                    help = _("time format code for <tt>creation-time</tt> as returned by api:"
                             "<br>v7: <tt>%b/%d/%Y %H:%M:%S</tt> "
                             "<br>v8: <tt>%Y-%m-%d %H:%M:%S</tt> "
                             "<br>leave empty for autodetection"),
                    allow_empty = False,
                    default_value = '',
                )
            )
         ],
    )

rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="mikrotik_file",
        group=RulespecGroupCheckParametersApplications,
        item_spec=_item_spec_mikrotik_file,
        parameter_valuespec=_parameter_valuespec_mikrotik_file,
        title=lambda: _("MikroTik File"),
    )
)


def _item_spec_mikrotik_ipsec():
    return TextAscii(title=_("MikroTik IPsec"))

def _parameter_valuespec_mikrotik_ipsec():
    return Dictionary(
        title    = _("MikroTik IPsec"),
        help     = _("Activate special agent mikrotik to use this."),
        elements = [
            ("ok_states",
                 ListOfStrings(
                     title = "Security Association states considered OK",
                     default_value = ['dying', 'mature'],
                     help = _("states that are OK."),
                 )
            ),
         ],
    )

rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="mikrotik_ipsec",
        group=RulespecGroupCheckParametersApplications,
        item_spec=_item_spec_mikrotik_ipsec,
        parameter_valuespec=_parameter_valuespec_mikrotik_ipsec,
        title=lambda: _("MikroTik IPsec"),
    )
)


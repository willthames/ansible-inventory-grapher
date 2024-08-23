#!/usr/bin/env python

# (c) 2014, Will Thames <will@thames.id.au>
#
# ansible-inventory-grapher is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ansible-inventory-grapher is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ansible-inventory-grapher.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import jinja2
import optparse
import os
import sys
from ansible import constants

import ansibleinventorygrapher.inventory
from ansibleinventorygrapher.version import __version__


DEFAULT_TEMPLATE = """digraph {{pattern|labelescape}} {
  {{ attributes }}

{% for node in nodes|sort(attribute='name') %}
{% if node.leaf %}
  {{ node.name|labelescape }} [shape=record style=rounded label=<
<table border="0" cellborder="0">
  <tr><td><b>
  <font face="Times New Roman, Bold" point-size="16">{{ node.name}}</font>
  </b></td></tr>
{% if node.vars and showvars %}<hr/><tr><td><font face="Times New Roman, Bold" point-size="14">{% for var in
   node.vars|sort %}{{var}}{% if var|is_visible %} = {{node.vars[var]}}{% endif %}<br/>{%
   endfor %}</font></td></tr>{% endif %}
</table>
>]
{% else %}
  {{ node.name|labelescape }} [shape=record label=<
<table border="0" cellborder="0">
  <tr><td><b>
  <font face="Times New Roman, Bold" point-size="16">{{ node.name}}</font>
  </b></td></tr>
{% if node.vars and showvars %}<hr/><tr><td><font face="Times New Roman, Bold" point-size="14">{% for
   var in node.vars|sort %}{{var}}{% if var|is_visible %} = {{node.vars[var]}}{% endif %}<br/>{%
   endfor %}</font></td></tr>{% endif %}
</table>
>]
{% endif %}{% endfor %}

{% for edge in edges|sort(attribute='source') %}
  {{ edge.source|labelescape }} -> {{ edge.target|labelescape }};
{% endfor %}
}

"""


def options_parser():
    usage = "%prog [options] pattern1 [pattern2 ...]"
    parser = optparse.OptionParser(usage=usage, version="%prog " + __version__)
    parser.add_option(
        "-i",
        dest="inventory",
        help="specify inventory host file [%default]",
        default=constants.DEFAULT_HOST_LIST,
    )
    parser.add_option(
        "-d",
        dest="directory",
        help="Location to output resulting files [current directory]",
        default=os.getcwd(),
    )
    parser.add_option(
        "-o",
        "--format",
        dest="format",
        default="-",
        help="python format string to name output files "
        + "(e.g. {}.dot) [defaults to stdout]",
    )
    parser.add_option(
        "-q",
        "--no-variables",
        dest="showvars",
        action="store_false",
        default=True,
        help="Turn off variable display in default template",
    )
    parser.add_option(
        "-t", dest="template", help="path to jinja2 template used for creating output"
    )
    parser.add_option(
        "-T", dest="print_template", action="store_true", help="print default template"
    )
    parser.add_option(
        "-a",
        dest="attributes",
        help="include top-level graphviz attributes from "
        + "http://www.graphviz.org/doc/info/attrs.html [%default]",
        default="rankdir=TB;",
    )
    parser.add_option(
        "--ask-vault-pass",
        dest="ask_vault_pass",
        default=constants.DEFAULT_ASK_VAULT_PASS,
        action="store_true",
        help="prompt for vault password",
    )
    parser.add_option(
        "--vault-password-file",
        dest="vault_password_files",
        help="vault password file",
        action="append",
        type="string",
    )
    parser.add_option(
        "--vault-id",
        default=[],
        dest="vault_ids",
        action="append",
        type="string",
        help="the vault identity to use",
    )
    parser.add_option(
        "--visible-vars",
        default=[],
        dest="visible_vars",
        action="append",
        type="string",
        help="Show value of a specific variable. Repeat for multiple variables",
    )
    parser.add_option(
        "--show-all-values",
        default=[],
        dest="all_vars_visible",
        action="store_true",
        help="Show values of all variables",
    )
    return parser


def labelescape(name):
    return '"%s"' % name.replace("-", "_").replace(".", "_")


def load_template(options):
    def is_visible(name):
        return options.all_vars_visible or name in options.visible_vars

    env = jinja2.Environment(
        trim_blocks=True, loader=jinja2.FileSystemLoader(os.getcwd())
    )
    env.filters["labelescape"] = labelescape
    env.filters["is_visible"] = is_visible

    if options.template:
        template = env.get_template(options.template)
    else:
        template = env.from_string(DEFAULT_TEMPLATE)
    return template


def render_graph(pattern, options):
    try:
        inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(
            options.inventory,
            options.ask_vault_pass,
            options.vault_password_files,
            options.vault_ids,
        )
    except ansibleinventorygrapher.inventory.NoVaultSecretFound:
        raise SystemExit("Couldn't find a secret to decrypt vaulted file(s)")

    hosts = inventory_mgr.inventory.list_hosts(pattern)
    template = load_template(options)
    if not hosts:
        print("No hosts matched for pattern %s" % pattern, file=sys.stderr)
        return
    if not os.path.exists(options.directory):
        os.makedirs(options.directory)
    edges = set()
    nodes = set()
    for host in hosts:
        try:
            (host_edges, host_nodes) = ansibleinventorygrapher.generate_graph_for_host(
                host, inventory_mgr
            )
        except ansibleinventorygrapher.inventory.NoVaultSecretFound:
            raise SystemExit("Couldn't find a secret to decrypt vaulted file(s)")
        edges |= host_edges
        nodes |= host_nodes
    output = template.render(
        edges=edges,
        nodes=nodes,
        pattern=pattern,
        attributes=options.attributes,
        showvars=options.showvars,
    )
    if options.format != "-":
        filename = options.format.format(pattern)
        fullpath = os.path.join(options.directory, filename)
        with open(fullpath, "w") as f:
            f.write(output)
    else:
        sys.stdout.write(output)


def main():
    parser = options_parser()
    (options, args) = parser.parse_args()
    if options.print_template:
        print(DEFAULT_TEMPLATE)
    if not args:
        parser.print_help()
        return 1
    for arg in args:
        render_graph(arg, options)
    return 0


if __name__ == "__main__":
    sys.exit(main())

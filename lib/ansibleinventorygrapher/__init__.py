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

import inspect

# Cache for parent graph lookups
_parents = dict()

# Cache for variables
_vars = dict()


class Edge(object):
    def __init__(self, source, target):
        self.source = source
        self.target = target

    def __repr__(self):
        return "{} -> {}".format(self.source, self.target)

    def __eq__(self, other):
        return self.source == other.source and self.target == other.target

    def __hash__(self):
        return hash(self.source + self.target)


class Node(object):
    def __init__(self, name, vars={}, leaf=False):
        self.name = name
        self.leaf = leaf
        self.vars = vars

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


def handle_missing_return_result(fn, member):
    # http://stackoverflow.com/a/197053
    vars = inspect.getargspec(fn)
    if 'return_results' in vars[0]:
        return fn(member, return_results=True)
    else:
        return fn(member)


def get_group_vars(group, inventory):
    return handle_missing_return_result(inventory.get_group_vars, group)


def get_host_vars(host, inventory):
    return handle_missing_return_result(inventory.get_host_vars, host)


def parent_graphs(child, groups):
    results = _parents.get(child.name, list())
    if not results:
        for group in groups:
            # For all other groups, if its parents contain this group, then
            # don't add this group as an edge
            if not any([group in g.parent_groups for g in groups if g != group]):
                results.append(Edge(group.name, child.name))
            if group.parent_groups:
                results.extend(parent_graphs(group, group.parent_groups))
        _parents[child.name] = results
    return results


def remove_inherited_and_overridden_vars(vars, group, inventory):
    if group not in _vars:
        _vars[group] = get_group_vars(group, inventory)
    gv = _vars[group]
    for (k, v) in vars.items():
        if k in gv:
            if gv[k] == v:
                vars.pop(k)
            else:
                gv.pop(k)


def remove_inherited_and_overridden_group_vars(group, inventory):
    if group not in _vars:
        _vars[group] = get_group_vars(group, inventory)
    for ancestor in group.get_ancestors():
        remove_inherited_and_overridden_vars(_vars[group], ancestor, inventory)


def tidy_all_the_variables(host, inventory):
    ''' removes all overridden and inherited variables from hosts
        and groups '''
    _vars[host] = get_host_vars(host, inventory)
    for group in host.get_groups():
        remove_inherited_and_overridden_vars(_vars[host], group, inventory)
        remove_inherited_and_overridden_group_vars(group, inventory)
    return _vars


def generate_graph_for_host(host, inventory):
    # dedup graph edges
    edges = set(parent_graphs(host, host.groups))
    vars = tidy_all_the_variables(host, inventory)
    nodes = set()
    nodes.add(Node(host.name, vars=vars[host], leaf=True))

    for group in host.get_groups():
        nodes.add(Node(group.name, vars=vars[group]))

    return (edges, nodes)

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


def parent_graphs(child, groups):
    results = _parents.get(child.name, list())
    # Remove 'all' group from groups if a child has any other parent group
    if len(groups) > 1:
        allgroups = [g for g in groups if g.name == 'all']
        if allgroups:
            groups.remove(allgroups[0])
    if not results:
        for group in groups:
            results.append(Edge(group.name, child.name))
            if group.parent_groups:
                results.extend(parent_graphs(group, group.parent_groups))
        _parents[child.name] = results
    return results


def remove_inherited_and_overridden_vars(vars, group):
    if group not in _vars:
        _vars[group] = group.vars.copy()
    gv = _vars[group]
    for (k, v) in vars.items():
        if k in gv:
            if gv[k] == v:
                vars.pop(k)
            else:
                gv.pop(k)


def remove_inherited_and_overridden_group_vars(group):
    if group not in _vars:
        _vars[group] = group.vars.copy()
    for ancestor in group.get_ancestors():
        remove_inherited_and_overridden_vars(_vars[group], ancestor)


def tidy_all_the_variables(host):
    ''' removes all overridden and inherited variables from hosts
        and groups '''
    _vars[host] = host.vars.copy()
    for group in host.get_groups():
        remove_inherited_and_overridden_vars(_vars[host], group)
        remove_inherited_and_overridden_group_vars(group)
    return _vars


def generate_graph_for_host(host):
    # dedup graph edges
    edges = set(parent_graphs(host, host.groups))
    vars = tidy_all_the_variables(host)
    nodes = set()
    nodes.add(Node(host.name, vars=vars[host], leaf=True))

    for group in host.get_groups():
        nodes.add(Node(group.name, vars=vars[group]))

    return (edges, nodes)

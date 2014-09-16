import os
import sys
import unittest

import ansible.inventory
import ansibleinventorygrapher


class TestVars(unittest.TestCase):

    def setUp(self):
        invfile = os.path.join('test', 'inventory', 'hosts')
        self.inventory = ansible.inventory.Inventory(invfile)
        self.host = self.inventory.get_host("host")
        self.vars = grapher.tidy_all_the_variables(self.host)

    def test_gp_group_vars(self):
        gp = self.inventory.get_group("grandparent")
        vars = self.vars[gp]
        self.assertEqual(vars.keys(), ["gp_not_overridden"])
        self.assertEqual(vars["gp_not_overridden"], "gp")

    def test_parent_group_vars(self):
        parent = self.inventory.get_group("parent")
        vars = self.vars[parent]
        self.assertEqual(set(vars.keys()), set(["parent_not_overridden",
                         "gp_overridden_in_parent"]))
        self.assertEqual(vars["parent_not_overridden"], "parent")

    def test_host_vars(self):
        vars = self.vars[self.host]
        self.assertEqual(vars["gp_overridden_in_child"], "child")
        self.assertEqual(vars["parent_overridden_in_child"], "child")
        self.assertEqual(vars["child_only"], "child")


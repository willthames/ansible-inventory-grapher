import os
import sys
import unittest

import ansible.inventory
import ansibleinventorygrapher
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager

class TestVars(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        variable_manager = VariableManager()
        loader = DataLoader()
        invfile = os.path.join('test', 'inventory', 'hosts')
        cls.inventory = ansible.inventory.Inventory(loader=loader, variable_manager=variable_manager, host_list=invfile)
        variable_manager.set_inventory(cls.inventory)
        cls.host = cls.inventory.get_host("host")
        cls.vars = ansibleinventorygrapher.tidy_all_the_variables(cls.host)

    def test_gp_group_vars(self):
        gp = self.inventory.get_group("grandparent")
        gvars = self.vars[gp].copy()
        self.assertEqual(gvars.keys(), ["gp_not_overridden"])
        self.assertEqual(gvars["gp_not_overridden"], "gp")

    def test_parent_group_vars(self):
        parent = self.inventory.get_group("parent")
        pvars = self.vars[parent].copy()
        self.assertEqual(set(pvars.keys()), set(["parent_not_overridden",
                         "gp_overridden_in_parent"]))
        self.assertEqual(pvars["parent_not_overridden"], "parent")

    def test_host_vars(self):
        hvars = self.vars[self.host].copy()
        self.assertEqual(hvars["gp_overridden_in_child"], "child")
        self.assertEqual(hvars["parent_overridden_in_child"], "child")
        self.assertEqual(hvars["child_only"], "child")


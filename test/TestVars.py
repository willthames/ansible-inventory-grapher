import os
import unittest

import ansibleinventorygrapher.inventory


class TestVars(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        invfile = os.path.join('test', 'inventory', 'hosts')
        cls.inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(invfile)
        cls.host = cls.inventory_mgr.inventory.get_host("host")
        cls.vars = ansibleinventorygrapher.tidy_all_the_variables(cls.host, cls.inventory_mgr)

    def test_gp_group_vars(self):
        gp = self.inventory_mgr.inventory.get_group("grandparent")
        gvars = self.vars[gp]
        self.assertEqual(gvars.keys(), ["gp_not_overridden"])
        self.assertEqual(gvars["gp_not_overridden"], "gp")

    def test_parent_group_vars(self):
        parent = self.inventory_mgr.inventory.get_group("parent")
        pvars = self.vars[parent]
        self.assertEqual(set(pvars.keys()), set(["parent_not_overridden",
                         "gp_overridden_in_parent"]))
        self.assertEqual(pvars["parent_not_overridden"], "parent")

    def test_host_vars(self):
        hvars = self.vars[self.host].copy()
        self.assertEqual(hvars["gp_overridden_in_child"], "child")
        self.assertEqual(hvars["parent_overridden_in_child"], "child")
        self.assertEqual(hvars["child_only"], "child")

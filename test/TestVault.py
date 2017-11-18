import os
import unittest

import ansibleinventorygrapher.inventory


class TestVault(unittest.TestCase):

    def test_vault_password_file(self):
        invfile = os.path.join('test', 'vault', 'inventory')
        vault_password_files = [os.path.join('test', 'vault', 'vaultpass')]
        inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(invfile, False, vault_password_files)
        hostname = "web-01"
        host = inventory_mgr.inventory.get_host(hostname)
        group = inventory_mgr.inventory.get_group("web")
        the_vars = ansibleinventorygrapher.tidy_all_the_variables(host, inventory_mgr)
        self.assertEqual(the_vars[group]["text"], "hello")

    def test_vault_password_file(self):
        invfile = os.path.join('test', 'vault', 'inventory')
        vault_password_files = [os.path.join('test', 'vault', 'vaultpass'),
                                os.path.join('test', 'vault', 'notthevaultpass')]
        try:
            inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(invfile, False, vault_password_files)
            hostname = "web-01"
            host = inventory_mgr.inventory.get_host(hostname)
            group = inventory_mgr.inventory.get_group("web")
            the_vars = ansibleinventorygrapher.tidy_all_the_variables(host, inventory_mgr)
            self.assertEqual(the_vars[group]["text"], "hello")
        except NotImplementedError:
            pass  # ansible-vault only supports multiple vault password files from 2.4

    def test_vault_ids(self):
        invfile = os.path.join('test', 'vault_ids', 'inventory')
        vault_ids = ['another_vault@' + os.path.join('test', 'vault_ids', 'vaultpass')]
        try:
            inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(invfile, False, [], vault_ids)
            hostname = "web-01"
            host = inventory_mgr.inventory.get_host(hostname)
            the_vars = ansibleinventorygrapher.tidy_all_the_variables(host, inventory_mgr)
            self.assertEqual(the_vars[host]["hello"], "world")
        except NotImplementedError:
            pass  # ansible-vault only supports vault-id from 2.4


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

import ansible.inventory
import ansible.constants as C


class NoVaultSecretFound(Exception):
    pass


class Inventory(object):
    def __init__(self):
        self.vault_pass = None

    def get_host(self, host):
        return self.inventory.get_host(host)

    def list_hosts(self, pattern):
        return self.inventory.list_hosts(pattern)


class Inventory19(Inventory):

    def __init__(self, inventory, ask_vault_pass, vault_password_files, vault_ids):
        if vault_ids or len(vault_password_files) > 1:
            raise NotImplementedError
        from ansible import utils
        super(Inventory19, self).__init__()
        if ask_vault_pass:
            self.vault_pass = utils.ask_passwords(ask_vault_pass=True)[2]
        elif vault_password_files:
            self.vault_pass = utils.read_vault_file(vault_password_files[0])
        try:
            self.inventory = ansible.inventory.Inventory(inventory, vault_password=self.vault_pass)
        except ansible.errors.AnsibleError:
            raise NoVaultSecretFound

        self.variable_manager = None

    def get_group_vars(self, group):
        return self.inventory.get_group_vars(group)

    def get_host_vars(self, host):
        return self.inventory.get_host_vars(host)

    def get_group(self, group_name):
        return self.inventory.get_group(group_name)


class Inventory20(Inventory):

    def __init__(self, inventory, ask_vault_pass, vault_password_files, vault_ids):
        if vault_ids or len(vault_password_files) > 1:
            raise NotImplementedError
        from ansible.cli import CLI
        super(Inventory20, self).__init__()
        loader = DataLoader()
        if ask_vault_pass:
            self.vault_pass = CLI.ask_vault_passwords()
        elif vault_password_files:
            self.vault_pass = CLI.read_vault_password_file(vault_password_files[0], loader)
        if self.vault_pass is not None:
            loader.set_vault_password(self.vault_pass)
        self.variable_manager = VariableManager()
        try:
            self.inventory = ansible.inventory.Inventory(loader=loader,
                                                         variable_manager=self.variable_manager,
                                                         host_list=inventory)
        except ansible.errors.AnsibleError:
            raise NoVaultSecretFound
        self.variable_manager.set_inventory(self.inventory)

    def _handle_missing_return_result(self, fn, member):
        import inspect
        # http://stackoverflow.com/a/197053
        vars = inspect.getargspec(fn)
        if 'return_results' in vars[0]:
            return fn(member, return_results=True)
        else:
            return fn(member)

    def get_group_vars(self, group):
        return self._handle_missing_return_result(self.inventory.get_group_vars, group)

    def get_host_vars(self, host):
        return self._handle_missing_return_result(self.inventory.get_host_vars, host)

    def get_group(self, group_name):
        return self.inventory.get_group(group_name)


class Inventory24(Inventory):

    def __init__(self, inventory, ask_vault_pass, vault_password_files, vault_ids):
        from ansible.cli import CLI
        super(Inventory24, self).__init__()
        loader = DataLoader()
        if vault_ids or vault_password_files or ask_vault_pass:
            CLI.setup_vault_secrets(loader, vault_ids, vault_password_files, ask_vault_pass)
        self.inventory = ansible.inventory.manager.InventoryManager(loader=loader, sources=inventory)
        self.variable_manager = VariableManager(loader=loader)
        self.variable_manager.set_inventory(self.inventory)

    # internal fuctions that actually do the work
    # adapted almost entirely from lib/ansible/vars/manager.py
    def _plugins_inventory(self, entities):
        import os
        from ansible.plugins.loader import vars_loader
        from ansible.utils.vars import combine_vars
        ''' merges all entities by inventory source '''
        data = {}
        for inventory_dir in self.variable_manager._inventory._sources:
            if ',' in inventory_dir:  # skip host lists
                continue
            elif not os.path.isdir(inventory_dir):  # always pass 'inventory directory'
                inventory_dir = os.path.dirname(inventory_dir)

            for plugin in vars_loader.all():
                data = combine_vars(data, self._get_plugin_vars(plugin, inventory_dir, entities))
        return data

    def _get_plugin_vars(self, plugin, path, entities):
        from ansible.inventory.host import Host
        data = {}
        try:
            data = plugin.get_vars(self.variable_manager._loader, path, entities)
        except AttributeError:
            for entity in entities:
                if isinstance(entity, Host):
                    data.update(plugin.get_host_vars(entity.name))
                else:
                    data.update(plugin.get_group_vars(entity.name))
        return data

    def get_group_vars(self, group):
        return self._plugins_inventory([group])

    def get_host_vars(self, host):
        try:
            all_vars = self.variable_manager.get_vars(host=host, include_hostvars=True)
        except ansible.errors.AnsibleParserError:
            raise NoVaultSecretFound
        # play, host, task, include_hostvars, include_delegate_to
        magic_vars = ['ansible_playbook_python', 'groups', 'group_names', 'inventory_dir',
                      'inventory_file', 'inventory_hostname', 'inventory_hostname_short',
                      'omit', 'playbook_dir']
        return {k: v for (k, v) in all_vars.items() if k not in magic_vars}

    def get_group(self, group_name):
        return self.inventory.groups[group_name]


class InventoryManager(object):
    def __init__(self, inventory, ask_vault_pass=False, vault_password_files=None, vault_ids=None):
        if not vault_password_files:
            vault_password_files = []
            if C.DEFAULT_VAULT_PASSWORD_FILE:
                vault_password_files.append(C.DEFAULT_VAULT_PASSWORD_FILE)
        if not vault_ids:
            vault_ids = []
        self.inventory = INVENTORY(inventory, ask_vault_pass, vault_password_files, vault_ids)


try:
    from ansible.parsing.dataloader import DataLoader
    try:
        from ansible.vars.manager import VariableManager
        import ansible.inventory.manager
        INVENTORY = Inventory24
    except ImportError:
        from ansible.vars import VariableManager
        INVENTORY = Inventory20
except ImportError:
    INVENTORY = Inventory19

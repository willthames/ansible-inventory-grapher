import os
import pytest

from ansible.parsing.vault import VaultSecretsContext

import ansibleinventorygrapher.inventory


@pytest.fixture
def zap_vault_secrets_context():
    if VaultSecretsContext._current:
        VaultSecretsContext._current = None


def test_vault_password_file(zap_vault_secrets_context):
    invfile = os.path.join("test", "vault", "inventory")
    vault_password_files = [os.path.join("test", "vault", "vaultpass")]
    inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(
        invfile, False, vault_password_files
    )
    hostname = "web-01"
    host = inventory_mgr.inventory.get_host(hostname)
    group = inventory_mgr.inventory.get_group("web")
    the_vars = ansibleinventorygrapher.tidy_all_the_variables(host, inventory_mgr)
    assert the_vars[group]["text"] == "hello"


def test_vault_ids(zap_vault_secrets_context):
    invfile = os.path.join("test", "vault_ids", "inventory")
    vault_ids = ["another_vault@" + os.path.join("test", "vault_ids", "vaultpass")]
    inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(
        invfile, False, [], vault_ids
    )
    hostname = "web-01"
    host = inventory_mgr.inventory.get_host(hostname)
    the_vars = ansibleinventorygrapher.tidy_all_the_variables(host, inventory_mgr)
    assert the_vars[host]["hello"] == "world"


def test_no_vault_pass(zap_vault_secrets_context):
    invfile = os.path.join("test", "vault", "inventory")
    try:
        inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(
            invfile, False, []
        )
        hostname = "web-01"
        host = inventory_mgr.inventory.get_host(hostname)
        ansibleinventorygrapher.tidy_all_the_variables(
            host, inventory_mgr
        )
        raise RuntimeError
    except ansibleinventorygrapher.inventory.NoVaultSecretFound:
        pass  # expected behaviour


def test_inline_vault_without_password(zap_vault_secrets_context):
    invfile = os.path.join("test", "vault", "inventory")
    inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(
        invfile, False, []
    )
    hostname = "inline-01"
    host = inventory_mgr.inventory.get_host(hostname)
    group = inventory_mgr.inventory.get_group("inline")
    the_vars = ansibleinventorygrapher.tidy_all_the_variables(host, inventory_mgr)
    assert "text" in the_vars[group]
    assert "text" not in the_vars[host]

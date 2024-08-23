import os
import pytest

import ansibleinventorygrapher.inventory


def test_vault_password_file():
    invfile = os.path.join("tests", "vault", "inventory")
    vault_password_files = [os.path.join("tests", "vault", "vaultpass")]
    inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(
        invfile, False, vault_password_files
    )
    hostname = "web-01"
    host = inventory_mgr.inventory.get_host(hostname)
    group = inventory_mgr.inventory.get_group("web")
    the_vars = ansibleinventorygrapher.tidy_all_the_variables(host, inventory_mgr)
    assert the_vars[group]["text"] == "hello"


def test_vault_password_files():
    invfile = os.path.join("tests", "vault", "inventory")
    vault_password_files = [
        os.path.join("tests", "vault", "vaultpass"),
        os.path.join("tests", "vault", "notthevaultpass"),
    ]
    inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(
        invfile, False, vault_password_files
    )
    hostname = "web-01"
    host = inventory_mgr.inventory.get_host(hostname)
    group = inventory_mgr.inventory.get_group("web")
    the_vars = ansibleinventorygrapher.tidy_all_the_variables(host, inventory_mgr)
    assert the_vars[group]["text"] == "hello"


def test_vault_ids():
    invfile = os.path.join("tests", "vault_ids", "inventory")
    vault_ids = ["another_vault@" + os.path.join("tests", "vault_ids", "vaultpass")]
    inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(
        invfile, False, [], vault_ids
    )
    hostname = "web-01"
    host = inventory_mgr.inventory.get_host(hostname)
    the_vars = ansibleinventorygrapher.tidy_all_the_variables(host, inventory_mgr)
    assert the_vars[host]["hello"] == "world"


def test_no_vault_pass():
    invfile = os.path.join("tests", "vault", "inventory")
    with pytest.raises(ansibleinventorygrapher.inventory.NoVaultSecretFound):
        inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(
            invfile, False, []
        )
        hostname = "web-01"
        host = inventory_mgr.inventory.get_host(hostname)
        ansibleinventorygrapher.tidy_all_the_variables(host, inventory_mgr)


def test_inline_vault_without_password():
    invfile = os.path.join("tests", "vault", "inventory")
    inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(
        invfile, False, []
    )
    hostname = "inline-01"
    host = inventory_mgr.inventory.get_host(hostname)
    group = inventory_mgr.inventory.get_group("inline")
    the_vars = ansibleinventorygrapher.tidy_all_the_variables(host, inventory_mgr)
    assert "text" in the_vars[group]
    assert "text" not in the_vars[host]

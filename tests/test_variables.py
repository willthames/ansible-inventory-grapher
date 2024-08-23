import os
import pytest

import ansibleinventorygrapher.inventory


@pytest.fixture
def inventory_mgr():
    invfile = os.path.join("tests", "inventory", "hosts")
    inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(invfile)
    yield inventory_mgr


@pytest.fixture
def host(inventory_mgr):
    yield inventory_mgr.inventory.get_host("host")


@pytest.fixture
def variables(inventory_mgr, host):
    yield ansibleinventorygrapher.tidy_all_the_variables(host, inventory_mgr)


def test_gp_group_vars(inventory_mgr, variables):
    gp = inventory_mgr.inventory.get_group("grandparent")
    gvars = variables[gp]
    assert set(gvars.keys()) == set(["gp_not_overridden"])
    assert gvars["gp_not_overridden"] == "gp"


def test_parent_group_vars(inventory_mgr, variables):
    parent = inventory_mgr.inventory.get_group("parent")
    pvars = variables[parent]
    assert set(pvars.keys()) == set(
        ["parent_not_overridden", "gp_overridden_in_parent"]
    )
    assert pvars["parent_not_overridden"] == "parent"


def test_host_vars(variables, host):
    hvars = variables[host].copy()
    assert hvars["gp_overridden_in_child"] == "child"
    assert hvars["parent_overridden_in_child"] == "child"
    assert hvars["child_only"] == "child"

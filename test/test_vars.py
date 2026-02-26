import os

import pytest

import ansibleinventorygrapher


class Inventory:
    def __init__(self):
        invfile = os.path.join("test", "inventory", "hosts")
        self.inventory_mgr = ansibleinventorygrapher.inventory.InventoryManager(invfile)
        self.host = self.inventory_mgr.inventory.get_host("host")
        self.vars = ansibleinventorygrapher.tidy_all_the_variables(
            self.host, self.inventory_mgr
        )


@pytest.fixture
def setup():
    return Inventory()


def test_gp_group_vars(setup):
    gp = setup.inventory_mgr.inventory.get_group("grandparent")
    gvars = setup.vars[gp]
    assert set(gvars.keys()) == set(["gp_not_overridden"])
    assert gvars["gp_not_overridden"] == "gp"


def test_parent_group_vars(setup):
    parent = setup.inventory_mgr.inventory.get_group("parent")
    pvars = setup.vars[parent]
    assert set(pvars.keys()) == set(["parent_not_overridden", "gp_overridden_in_parent"])
    assert pvars["parent_not_overridden"] == "parent"


def test_host_vars(setup):
    hvars = setup.vars[setup.host].copy()
    assert hvars["gp_overridden_in_child"] == "child"
    assert hvars["parent_overridden_in_child"] == "child"
    assert hvars["child_only"] == "child"

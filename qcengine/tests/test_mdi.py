"""
Tests the MDI interface
"""

import copy
import os

import pydantic
import pytest

import qcengine as qcng
from qcengine import testing
from qcengine.testing import environ_context
from qcelemental.testing import compare_values

_base_json = {"schema_name": "qcschema_input", "schema_version": 1}

@testing.using_psi4
@testing.using_mdi
def test_mdi_water():
    json_data = copy.deepcopy(_base_json)
    json_data["molecule"] = qcng.get_molecule("water")
    json_data["driver"] = "energy"
    json_data["model"] = {"method": "SCF", "basis": "sto-3g"}
    json_data["keywords"] = {"scf_type": "df"}

    engine = qcng.MDIServer("-role DRIVER -name QCEngine -method TEST", "psi4", 
                            qcng.get_molecule("water"),
                            {"method": "SCF", "basis": "sto-3g"},
                            {"scf_type": "df"})

    # Test the <NATOMS command
    natom = engine.send_natoms()
    assert natom == 3

    # Test the <COORDS command
    coords = engine.send_coords()
    expected = [ 0.0, 0.0, -0.12947694, 0.0, -1.49418734, 1.02744651, 0.0, 1.49418734, 1.02744651]
    assert compare_values(expected, coords, atol=1.e-7)

    # Test the >COORDS command
    expected = [ 0.1, 0.0, -0.12947694, 0.0, -1.49418734, 1.02744651, 0.0, 1.49418734, 1.02744651]
    engine.recv_coords(expected)
    coords = engine.send_coords()
    assert compare_values(expected, coords, atol=1.e-7)

    # Test the <ELEMENTS command
    elements = engine.send_elements()
    expected = [8.0, 1.0, 1.0]
    assert compare_values(expected, elements, atol=1.e-7)

    # Test the <MASSES command
    masses = engine.send_masses()
    expected = [15.99491461957, 1.00782503223, 1.00782503223]
    assert compare_values(expected, masses, atol=1.e-6)

    # Test the <ENERGY command
    energy = engine.send_energy()
    expected = -74.96475393
    assert compare_values(expected, energy, atol=1.e-6)

    # Test the <FORCES command
    forces = engine.send_forces()
    expected = [
        0.0, 0.0, -0.00073827952, 0.0, -0.020208584243, 0.00036913976, -0.0, 0.020208584243, 0.00036913976 ]
    assert compare_values(expected, forces, atol=1.e-6)

    # Test the >MASSES command
    expected = [15.99491461957, 1.00782503223, 1.00782503223]
    engine.recv_masses(expected)
    masses = engine.send_masses()
    assert compare_values(expected, masses, atol=1.e-7)

    # Test the <NCOMMANDS command
    ncommands = engine.send_ncommands()

    # Test the <COMMANDS command
    commands = engine.send_commands()

    # Test the <TOTCHARGE command
    totcharge = engine.send_total_charge()
    expected = 0.0
    assert compare_values(expected, totcharge, atol=1.e-7)

    # Test the <ELEC_MULT command
    multiplicity = engine.send_multiplicity()
    expected = 1
    assert compare_values(expected, multiplicity, atol=1.e-7)

    # Test the >TOTCHARGE and >ELEC_MULT commands
    expected = 1.0
    multiplicity = 2
    engine.recv_total_charge(expected)
    engine.recv_multiplicity(multiplicity)
    totcharge = engine.send_total_charge()
    assert compare_values(expected, totcharge, atol=1.e-7)

    # Test the final energy
    energy = engine.send_energy()
    expected = -74.66669841
    assert compare_values(expected, energy, atol=1.e-6)

    # Test the EXIT command
    engine.exit()

    return 0

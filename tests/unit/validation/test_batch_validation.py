# SPDX-FileCopyrightText: 2022 Contributors to the Power Grid Model project <dynamic.grid.calculation@alliander.com>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Dict

import numpy as np
import pytest
from power_grid_model import initialize_array
from power_grid_model.validation import validate_batch_data
from power_grid_model.validation.errors import MultiComponentNotUniqueError, NotBooleanError


@pytest.fixture
def input_data() -> Dict[str, np.ndarray]:
    node = initialize_array("input", "node", 4)
    node["id"] = [1, 2, 3, 4]
    node["u_rated"] = 10.5e3
    line = initialize_array("input", "line", 4)

    line["id"] = [5, 6, 7, 8]
    line["from_node"] = [1, 2, 3, 1]
    line["to_node"] = [2, 3, 1, 2]
    line["from_status"] = 0
    line["to_status"] = 0
    line["r1"] = 1.0
    line["x1"] = 2.0
    line["c1"] = 3.0
    line["tan1"] = 4.0
    line["i_n"] = 5.0
    return {"node": node, "line": line}


@pytest.fixture
def batch_data() -> Dict[str, np.ndarray]:
    line = initialize_array("update", "line", (3, 2))
    line["id"] = [[5, 6], [6, 7], [7, 5]]
    line["from_status"] = [[1, 1], [1, 1], [1, 1]]
    return {"line": line}


def test_validate_batch_data_input_error(input_data, batch_data):
    input_data["node"][-1]["id"] = 123
    input_data["line"][-1]["id"] = 123
    errors = validate_batch_data(input_data, batch_data)
    assert len(errors) == 3
    assert [MultiComponentNotUniqueError([("line", "id"), ("node", "id")], [("line", 123), ("node", 123)])] == errors[0]
    assert [MultiComponentNotUniqueError([("line", "id"), ("node", "id")], [("line", 123), ("node", 123)])] == errors[1]
    assert [MultiComponentNotUniqueError([("line", "id"), ("node", "id")], [("line", 123), ("node", 123)])] == errors[2]


def test_validate_batch_data_update_error(input_data, batch_data):
    batch_data["line"]["from_status"] = [[12, 34], [0, -128], [56, 78]]
    errors = validate_batch_data(input_data, batch_data)
    assert len(errors) == 2
    assert [NotBooleanError("line", "from_status", [5, 6])] == errors[0]
    assert [NotBooleanError("line", "from_status", [5, 7])] == errors[2]

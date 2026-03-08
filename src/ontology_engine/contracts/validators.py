"""
Contract Validators — Pre/postcondition enforcement.

Validates data at every node boundary using JSON Schema.
If validation fails, the pipeline halts.
"""

import jsonschema

from .schemas import NODE_1_TO_2_SCHEMA, NODE_2_TO_3_SCHEMA, NODE_3_TO_4_SCHEMA

SCHEMAS = {
    "node1_to_2": NODE_1_TO_2_SCHEMA,
    "node2_to_3": NODE_2_TO_3_SCHEMA,
    "node3_to_4": NODE_3_TO_4_SCHEMA,
}


class ContractViolation(Exception):
    """Raised when data fails inter-node contract validation."""
    pass


def validate_contract(data: dict, contract_name: str) -> bool:
    """Validate data against a named inter-node contract.

    Args:
        data: The data to validate.
        contract_name: One of 'node1_to_2', 'node2_to_3', 'node3_to_4'.

    Raises:
        ContractViolation: If validation fails.
        ValueError: If contract_name is unknown.

    Returns: True if validation passes.
    """
    schema = SCHEMAS.get(contract_name)
    if schema is None:
        raise ValueError(f"Unknown contract: {contract_name}")

    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        raise ContractViolation(
            f"Contract '{contract_name}' violated: {e.message}"
        ) from e

    return True

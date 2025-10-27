"""
inventory_system.py
Fixed version for static-analysis lab:
 - No mutable default arguments
 - Specific exception handling
 - No eval usage
 - Proper file handling
 - Input validation
 - Logging configured
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Global inventory dictionary (string -> int)
stock_data: Dict[str, int] = {}

def add_item(item: str = "default", qty: int = 0, logs: Optional[List[str]] = None) -> None:
    """
    Add qty of item to stock_data. logs is a local list to collect messages if provided.
    """
    if logs is None:
        logs = []

    if not item:
        raise ValueError("item must be a non-empty string")

    if not isinstance(item, str):
        raise TypeError("item must be a string")

    if not isinstance(qty, int):
        raise TypeError("qty must be an integer")

    if qty < 0:
        raise ValueError("qty must be non-negative")

    global stock_data
    stock_data[item] = stock_data.get(item, 0) + qty
    logs.append(f"{datetime.now()}: Added {qty} of {item}")
    logger.debug("Added %d of %s. New qty: %d", qty, item, stock_data[item])

def remove_item(item: str, qty: int) -> None:
    """
    Remove qty of item from stock_data. If item missing or qty invalid, raise appropriate exceptions.
    """
    if not isinstance(item, str):
        raise TypeError("item must be a string")

    if not isinstance(qty, int):
        raise TypeError("qty must be an integer")

    if qty < 0:
        raise ValueError("qty must be non-negative")

    if item not in stock_data:
        raise KeyError(f"Item '{item}' not found in inventory")

    if stock_data[item] < qty:
        raise ValueError(f"Not enough quantity of '{item}' to remove")

    stock_data[item] -= qty
    if stock_data[item] == 0:
        del stock_data[item]

    logger.debug("Removed %d of %s. Remaining: %s", qty, item, stock_data.get(item, 0))

def get_qty(item: str) -> int:
    """
    Return quantity for item (0 if not present).
    """
    if not isinstance(item, str):
        raise TypeError("item must be a string")
    return stock_data.get(item, 0)

def load_data(file: str = "inventory.json") -> None:
    """
    Load JSON inventory from file. If file missing, start with empty inventory.
    """
    global stock_data
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Inventory file must contain a JSON object")
            # Validate loaded values are integers
            validated: Dict[str, int] = {}
            for k, v in data.items():
                if not isinstance(k, str) or not isinstance(v, int):
                    raise ValueError("Inventory entries must be str->int")
                validated[k] = v
            stock_data = validated
            logger.info("Loaded inventory from %s", file)
    except FileNotFoundError:
        logger.warning("Inventory file %s not found. Starting with empty inventory.", file)
        stock_data = {}
    except json.JSONDecodeError as ex:
        logger.error("Failed to parse JSON file %s: %s", file, ex)
        raise
    except Exception:
        # Re-raise unexpected exceptions after logging
        logger.exception("Unexpected error while loading data from %s", file)
        raise

def save_data(file: str = "inventory.json") -> None:
    """
    Save current inventory to file using safe file writing.
    """
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(stock_data, f, indent=2, sort_keys=True)
        logger.info("Saved inventory to %s", file)
    except Exception:
        logger.exception("Failed to save inventory to %s", file)
        raise

def print_data() -> None:
    """Print a simple report of items."""
    print("Items Report")
    for name, qty in stock_data.items():
        print(f"{name} -> {qty}")

def check_low_items(threshold: int = 5) -> List[str]:
    """Return list of items with quantity less than threshold."""
    if not isinstance(threshold, int):
        raise TypeError("threshold must be an integer")
    return [name for name, qty in stock_data.items() if qty < threshold]

def main() -> None:
    """Sample run demonstrating API usage. Wrap risky operations with try/except at top level."""
    try:
        # Demonstrate adding & removing items
        add_item("apple", 10)
        # Do not allow negative addition — provide meaningful error handling
        try:
            add_item("banana", -2)
        except ValueError as exc:
            logger.warning("Could not add banana: %s", exc)

        # Demonstrate type validation
        try:
            add_item(123, 10)  # will raise TypeError
        except TypeError as exc:
            logger.warning("Invalid add_item call: %s", exc)

        remove_item("apple", 3)
        try:
            remove_item("orange", 1)
        except KeyError as exc:
            logger.info("Tried to remove non-existent item: %s", exc)

        print("Apple stock:", get_qty("apple"))
        print("Low items:", check_low_items())
        save_data()
        load_data()
        print_data()

        # Removed eval() for safety. If you want to run a fixed, controlled action, call the function directly.
        logger.info("Demo run complete")
    except Exception:
        logger.exception("Unhandled exception in main")

if __name__ == "__main__":
    main()
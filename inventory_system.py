"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: [Luke Jensen]

AI Usage: [Syntax Error Fixes, etc.]

This module handles inventory management, item usage, and equipment.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """Add item to character inventory"""
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    
    character["inventory"].append(item_id)
    return True


def remove_item_from_inventory(character, item_id):
    """Remove item from inventory"""
    if item_id not in character["inventory"]:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")
    
    character["inventory"].remove(item_id)
    return True


def has_item(character, item_id):
    """Check if item is in inventory"""
    return item_id in character["inventory"]


def count_item(character, item_id):
    """Count copies of item in inventory"""
    return character["inventory"].count(item_id)


def get_inventory_space_remaining(character):
    """Remaining inventory slots"""
    return MAX_INVENTORY_SIZE - len(character["inventory"])


def clear_inventory(character):
    """Clear inventory and return removed items"""
    removed = character["inventory"].copy()
    character["inventory"].clear()
    return removed

# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """Use a consumable item"""
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found.")
    
    if item_data["type"] != "consumable":
        raise InvalidItemTypeError("Only consumable items can be used.")

    stat, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, value)

    remove_item_from_inventory(character, item_id)

    return f"{character['name']} used {item_id} and gained {stat} +{value}."

# ============================================================================
# EQUIPMENT (WEAPONS & ARMOR)
# ============================================================================

def equip_weapon(character, item_id, item_data):
    """Equip a weapon"""
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found.")
    if item_data["type"] != "weapon":
        raise InvalidItemTypeError("Item is not a weapon.")

    # Unequip old weapon
    if character["equipped_weapon"] is not None:
        old = character["equipped_weapon"]
        old_stat, old_val = parse_item_effect(character["equipped_weapon_effect"])
        apply_stat_effect(character, old_stat, -old_val)
        add_item_to_inventory(character, old)

    # Equip new weapon
    stat, val = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, val)

    character["equipped_weapon"] = item_id
    character["equipped_weapon_effect"] = item_data["effect"]

    remove_item_from_inventory(character, item_id)
    return f"{character['name']} equipped weapon: {item_id} (+{val} {stat})"


def equip_armor(character, item_id, item_data):
    """Equip armor"""
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found.")
    if item_data["type"] != "armor":
        raise InvalidItemTypeError("Item is not armor.")

    # Unequip old armor
    if character["equipped_armor"] is not None:
        old = character["equipped_armor"]
        old_stat, old_val = parse_item_effect(character["equipped_armor_effect"])
        apply_stat_effect(character, old_stat, -old_val)
        add_item_to_inventory(character, old)

    # Equip new armor
    stat, val = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, val)

    character["equipped_armor"] = item_id
    character["equipped_armor_effect"] = item_data["effect"]

    remove_item_from_inventory(character, item_id)
    return f"{character['name']} equipped armor: {item_id} (+{val} {stat})"


def unequip_weapon(character):
    """Unequip weapon and return to inventory"""
    if character["equipped_weapon"] is None:
        return None

    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("No space to unequip weapon.")

    item_id = character["equipped_weapon"]
    stat, val = parse_item_effect(character["equipped_weapon_effect"])
    apply_stat_effect(character, stat, -val)

    add_item_to_inventory(character, item_id)

    character["equipped_weapon"] = None
    character["equipped_weapon_effect"] = None

    return item_id


def unequip_armor(character):
    """Unequip armor and return to inventory"""
    if character["equipped_armor"] is None:
        return None

    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("No space to unequip armor.")

    item_id = character["equipped_armor"]
    stat, val = parse_item_effect(character["equipped_armor_effect"])
    apply_stat_effect(character, stat, -val)

    add_item_to_inventory(character, item_id)

    character["equipped_armor"] = None
    character["equipped_armor_effect"] = None

    return item_id

# ============================================================================
# SHOP
# ============================================================================

def purchase_item(character, item_id, item_data):
    """Purchase an item from a shop"""
    cost = item_data["cost"]

    if character["gold"] < cost:
        raise InsufficientResourcesError("Not enough gold.")
    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Inventory is full.")

    character["gold"] -= cost
    add_item_to_inventory(character, item_id)

    return True


def sell_item(character, item_id, item_data):
    """Sell an item for half its value"""
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found.")

    value = item_data["cost"] // 2
    remove_item_from_inventory(character, item_id)
    character["gold"] += value

    return value

# ============================================================================
# HELPERS
# ============================================================================

def parse_item_effect(effect_string):
    """Convert 'stat:value' into ('stat', int(value))"""
    stat, value = effect_string.split(":")
    return stat.strip(), int(value)


def apply_stat_effect(character, stat_name, value):
    """Apply stat change with health cap logic"""
    character[stat_name] += value

    if stat_name == "health":
        character["health"] = min(character["health"], character["max_health"])


def display_inventory(character, item_data_dict):
    """
    Display formatted inventory.
    NOTE: unknown items will crash unless guaranteed valid by game.
    """
    print("\n=== INVENTORY ===")
    if not character["inventory"]:
        print("Inventory is empty.")
        return

    counted = {}
    for item_id in character["inventory"]:
        if item_id in counted:
            counted[item_id] += 1
        else:
            counted[item_id] = 1

    for item_id, qty in counted.items():
        item = item_data_dict[item_id]
        print(f"{item['name']} (x{qty}) - {item['type']}")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== INVENTORY SYSTEM TEST ===")

    
    # Test adding items
    # test_char = {'inventory': [], 'gold': 100, 'health': 80, 'max_health': 80}
    # 
    # try:
    #     add_item_to_inventory(test_char, "health_potion")
    #     print(f"Inventory: {test_char['inventory']}")
    # except InventoryFullError:
    #     print("Inventory is full!")
    
    # Test using items
    # test_item = {
    #     'item_id': 'health_potion',
    #     'type': 'consumable',
    #     'effect': 'health:20'
    # }
    # 
    # try:
    #     result = use_item(test_char, "health_potion", test_item)
    #     print(result)
    # except ItemNotFoundError:
    #     print("Item not found")


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
    """
    Add an item to character's inventory
    
    Args:
        character: Character dictionary
        item_id: Unique item identifier
    
    Returns: True if added successfully
    Raises: InventoryFullError if inventory is at max capacity
    """
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    
    character["inventory"].append(item_id)
    return True

def remove_item_from_inventory(character, item_id):
    """
    Remove an item from character's inventory
    
    Args:
        character: Character dictionary
        item_id: Item to remove
    
    Returns: True if removed successfully
    Raises: ItemNotFoundError if item not in inventory
    """
    if item_id not in character["inventory"]:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")
    
    character["inventory"].remove(item_id)
    return True

def has_item(character, item_id):
    """
    Check if character has a specific item
    
    Returns: True if item in inventory, False otherwise
    """
    return item_id in character["inventory"]

def count_item(character, item_id):
    """
    Count how many of a specific item the character has
    
    Returns: Integer count of item
    """
    return character["inventory"].count(item_id)

def get_inventory_space_remaining(character):
    """
    Calculate how many more items can fit in inventory
    
    Returns: Integer representing available slots
    """
    return MAX_INVENTORY_SIZE - len(character["inventory"])

def clear_inventory(character):
    """
    Remove all items from inventory
    
    Returns: List of removed items
    """
    removed = character["inventory"].copy()
    character["inventory"].clear()
    return removed

# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """
    Use a consumable item from inventory
    
    Args:
        character: Character dictionary
        item_id: Item to use
        item_data: Item information dictionary from game_data
    
    Item types and effects:
    - consumable: Apply effect and remove from inventory
    - weapon/armor: Cannot be "used", only equipped
    
    Returns: String describing what happened
    Raises: 
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'consumable'
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found.")
    
    if item_data["type"] != "consumable":
        raise InvalidItemTypeError("Only consumable items can be used.")
    
    stat, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, value)

    remove_item_from_inventory(character, item_id)

    return f"{character['name']} used {item_id} and gained {stat} +{value}."

def equip_weapon(character, item_id, item_data):
    """
    Equip a weapon
    
    Args:
        character: Character dictionary
        item_id: Weapon to equip
        item_data: Item information dictionary
    
    Weapon effect format: "strength:5" (adds 5 to strength)
    
    If character already has weapon equipped:
    - Unequip current weapon (remove bonus)
    - Add old weapon back to inventory
    
    Returns: String describing equipment change
    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'weapon'
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found.")

    if item_data["type"] != "weapon":
        raise InvalidItemTypeError("Item is not a weapon.")

    # Unequip current weapon if needed
    if "equipped_weapon" in character and character["equipped_weapon"] is not None:
        old_weapon = character["equipped_weapon"]
        old_stat, old_val = parse_item_effect(character["equipped_weapon_effect"])
        apply_stat_effect(character, old_stat, -old_val)

        # Add old weapon back
        add_item_to_inventory(character, old_weapon)

    # Equip new weapon
    stat, val = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, val)

    character["equipped_weapon"] = item_id
    character["equipped_weapon_effect"] = item_data["effect"]

    remove_item_from_inventory(character, item_id)

    return f"{character['name']} equipped weapon: {item_id} (+{val} {stat})"

def equip_armor(character, item_id, item_data):
    """
    Equip armor
    
    Args:
        character: Character dictionary
        item_id: Armor to equip
        item_data: Item information dictionary
    
    Armor effect format: "max_health:10" (adds 10 to max_health)
    
    If character already has armor equipped:
    - Unequip current armor (remove bonus)
    - Add old armor back to inventory
    
    Returns: String describing equipment change
    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'armor'
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found.")

    if item_data["type"] != "armor":
        raise InvalidItemTypeError("Item is not armor.")

    # Unequip old armor
    if "equipped_armor" in character and character["equipped_armor"] is not None:
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
    """
    Remove equipped weapon and return it to inventory
    
    Returns: Item ID that was unequipped, or None if no weapon equipped
    Raises: InventoryFullError if inventory is full
    """
    if "equipped_weapon" not in character or character["equipped_weapon"] is None:
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
    """
    Remove equipped armor and return it to inventory
    
    Returns: Item ID that was unequipped, or None if no armor equipped
    Raises: InventoryFullError if inventory is full
    """
    if "equipped_armor" not in character or character["equipped_armor"] is None:
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
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data):
    """
    Purchase an item from a shop
    
    Args:
        character: Character dictionary
        item_id: Item to purchase
        item_data: Item information with 'cost' field
    
    Returns: True if purchased successfully
    Raises:
        InsufficientResourcesError if not enough gold
        InventoryFullError if inventory is full
    """
    cost = item_data["cost"]

    if character["gold"] < cost:
        raise InsufficientResourcesError("Not enough gold.")
    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Inventory is full.")

    character["gold"] -= cost
    add_item_to_inventory(character, item_id)

    return True

def sell_item(character, item_id, item_data):
    """
    Sell an item for half its purchase cost
    
    Args:
        character: Character dictionary
        item_id: Item to sell
        item_data: Item information with 'cost' field
    
    Returns: Amount of gold received
    Raises: ItemNotFoundError if item not in inventory
    """
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not found.")

    sell_value = item_data["cost"] // 2
    remove_item_from_inventory(character, item_id)
    character["gold"] += sell_value

    return sell_value

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_item_effect(effect_string):
    """
    Parse item effect string into stat name and value
    
    Args:
        effect_string: String in format "stat_name:value"
    
    Returns: Tuple of (stat_name, value)
    Example: "health:20" → ("health", 20)
    """
    stat, value = effect_string.split(":")
    return stat, int(value)

def apply_stat_effect(character, stat_name, value):
    """
    Apply a stat modification to character
    
    Valid stats: health, max_health, strength, magic
    
    Note: health cannot exceed max_health
    """
    character[stat_name] += value
    
    if stat_name == "health":
        character["health"] = min(character["health"], character["max_health"])

def display_inventory(character, item_data_dict):
    """
    Display character's inventory in formatted way
    
    Args:
        character: Character dictionary
        item_data_dict: Dictionary of all item data
    
    Shows item names, types, and quantities
    """
    print("\n=== INVENTORY ===")
    if not character["inventory"]:
        print("Inventory is empty.")
        return

    counted = {}
    for item_id in character["inventory"]:
        counted[item_id] = counted.get(item_id, 0) + 1

    for item_id, qty in counted.items():
        item = item_data_dict.get(item_id, {"name": "Unknown", "type": "unknown"})
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


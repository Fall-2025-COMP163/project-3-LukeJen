"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

Name: [Luke Jensen]

AI Usage: [Bug Fixes]

This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_quests(filename="data/quests.txt"):
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Quest data file not found: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        raise CorruptedDataError(f"Could not read quest data file: {e}")

    blocks = [block.strip() for block in raw.split("\n\n") if block.strip()]
    quests = {}

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        try:
            q = parse_quest_block(lines)
        except InvalidDataFormatError as e:
            raise InvalidDataFormatError(f"Invalid quest block: {e}")

        quest_id = q["quest_id"]
        if quest_id in quests:
            raise InvalidDataFormatError(f"Duplicate quest id '{quest_id}' in file.")
        quests[quest_id] = q

    return quests


def load_items(filename="data/items.txt"):
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Item data file not found: {filename}")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            raw = f.read()
    except Exception as e:
        raise CorruptedDataError(f"Could not read item data file: {e}")

    blocks = [block.strip() for block in raw.split("\n\n") if block.strip()]
    items = {}

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        try:
            itm = parse_item_block(lines)
        except InvalidDataFormatError as e:
            raise InvalidDataFormatError(f"Invalid item block: {e}")

        item_id = itm["item_id"]
        if item_id in items:
            raise InvalidDataFormatError(f"Duplicate item id '{item_id}' in file.")
        items[item_id] = itm

    return items

# ============================================================================
# VALIDATION FUNCTIONS (NO .get() USED)
# ============================================================================

def validate_quest_data(quest_dict):
    required = {
        "quest_id", "title", "description", "reward_xp",
        "reward_gold", "required_level", "prerequisite"
    }

    missing = required - quest_dict.keys()
    if missing:
        raise InvalidDataFormatError(f"Missing quest fields: {', '.join(sorted(missing))}")

    # Direct access is safe because missing fields were already checked
    if not isinstance(quest_dict["reward_xp"], int):
        raise InvalidDataFormatError("Quest field 'reward_xp' must be an integer.")

    if not isinstance(quest_dict["reward_gold"], int):
        raise InvalidDataFormatError("Quest field 'reward_gold' must be an integer.")

    if not isinstance(quest_dict["required_level"], int):
        raise InvalidDataFormatError("Quest field 'required_level' must be an integer.")

    if not isinstance(quest_dict["prerequisite"], str):
        raise InvalidDataFormatError("Quest field 'prerequisite' must be a string.")

    return True


def validate_item_data(item_dict):
    required = {"item_id", "name", "type", "effect", "cost", "description"}

    missing = required - item_dict.keys()
    if missing:
        raise InvalidDataFormatError(f"Missing item fields: {', '.join(sorted(missing))}")

    if item_dict["type"] not in ("weapon", "armor", "consumable"):
        raise InvalidDataFormatError(f"Invalid item type: {item_dict['type']}")

    if not isinstance(item_dict["cost"], int):
        raise InvalidDataFormatError("Item field 'cost' must be an integer.")

    eff = item_dict["effect"]
    if ":" not in eff:
        raise InvalidDataFormatError("Item 'effect' must use format 'stat:value'.")

    stat, val = eff.split(":", 1)
    stat = stat.strip()
    val = val.strip()

    if not stat or not val:
        raise InvalidDataFormatError("Item 'effect' must contain both stat and value.")

    try:
        int(val)
    except ValueError:
        raise InvalidDataFormatError("Item effect value must be an integer.")

    return True

# ============================================================================
# DEFAULT FILE CREATOR
# ============================================================================

def create_default_data_files():
    data_dir = "data"
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir, exist_ok=True)
        except Exception as e:
            raise CorruptedDataError(f"Could not create data directory: {e}")

    quests_path = os.path.join(data_dir, "quests.txt")
    items_path = os.path.join(data_dir, "items.txt")

    if not os.path.exists(quests_path):
        default_quests = """QUEST_ID: first_quest
TITLE: First Steps
DESCRIPTION: Prove yourself by completing this simple task.
REWARD_XP: 50
REWARD_GOLD: 25
REQUIRED_LEVEL: 1
PREREQUISITE: NONE

QUEST_ID: goblin_menace
TITLE: Goblin Menace
DESCRIPTION: Clear out the goblins troubling the nearby farms.
REWARD_XP: 100
REWARD_GOLD: 50
REQUIRED_LEVEL: 2
PREREQUISITE: first_quest
"""
        try:
            with open(quests_path, "w", encoding="utf-8") as f:
                f.write(default_quests)
        except Exception as e:
            raise CorruptedDataError(f"Could not create default quests file: {e}")

    if not os.path.exists(items_path):
        default_items = """ITEM_ID: health_potion
NAME: Health Potion
TYPE: consumable
EFFECT: health:30
COST: 25
DESCRIPTION: Restores a moderate amount of health.

ITEM_ID: iron_sword
NAME: Iron Sword
TYPE: weapon
EFFECT: strength:5
COST: 100
DESCRIPTION: A basic sword that increases strength.

ITEM_ID: leather_armor
NAME: Leather Armor
TYPE: armor
EFFECT: max_health:10
COST: 80
DESCRIPTION: Basic armor that increases maximum health.
"""
        try:
            with open(items_path, "w", encoding="utf-8") as f:
                f.write(default_items)
        except Exception as e:
            raise CorruptedDataError(f"Could not create default items file: {e}")

    return True

# ============================================================================
# PARSERS (UNCHANGED EXCEPT NO .get())
# ============================================================================

def parse_quest_block(lines):
    data = {}
    for line in lines:
        if ":" not in line:
            raise InvalidDataFormatError(f"Malformed line: '{line}' (expected 'KEY: value').")

        key, value = line.split(":", 1)
        key = key.strip().upper()
        value = value.strip()

        if key == "QUEST_ID":
            data["quest_id"] = value
        elif key == "TITLE":
            data["title"] = value
        elif key == "DESCRIPTION":
            data["description"] = value
        elif key == "REWARD_XP":
            try:
                data["reward_xp"] = int(value)
            except ValueError:
                raise InvalidDataFormatError("REWARD_XP must be an integer.")
        elif key == "REWARD_GOLD":
            try:
                data["reward_gold"] = int(value)
            except ValueError:
                raise InvalidDataFormatError("REWARD_GOLD must be an integer.")
        elif key == "REQUIRED_LEVEL":
            try:
                data["required_level"] = int(value)
            except ValueError:
                raise InvalidDataFormatError("REQUIRED_LEVEL must be an integer.")
        elif key == "PREREQUISITE":
            data["prerequisite"] = value

    validate_quest_data(data)
    return data


def parse_item_block(lines):
    data = {}
    for line in lines:
        if ":" not in line:
            raise InvalidDataFormatError(f"Malformed line: '{line}' (expected 'KEY: value').")

        key, value = line.split(":", 1)
        key = key.strip().upper()
        value = value.strip()

        if key == "ITEM_ID":
            data["item_id"] = value
        elif key == "NAME":
            data["name"] = value
        elif key == "TYPE":
            data["type"] = value.lower()
        elif key == "EFFECT":
            data["effect"] = value
        elif key == "COST":
            try:
                data["cost"] = int(value)
            except ValueError:
                raise InvalidDataFormatError("COST must be an integer.")
        elif key == "DESCRIPTION":
            data["description"] = value

    validate_item_data(data)
    return data

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    
    # Test creating default files
    # create_default_data_files()
    
    # Test loading quests
    # try:
    #     quests = load_quests()
    #     print(f"Loaded {len(quests)} quests")
    # except MissingDataFileError:
    #     print("Quest file not found")
    # except InvalidDataFormatError as e:
    #     print(f"Invalid quest format: {e}")
    
    # Test loading items
    # try:
    #     items = load_items()
    #     print(f"Loaded {len(items)} items")
    # except MissingDataFileError:
    #     print("Item file not found")
    # except InvalidDataFormatError as e:
    #     print(f"Invalid item format: {e}")


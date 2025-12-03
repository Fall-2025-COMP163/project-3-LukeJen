"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Starter Code

Name: [Luke Jensen]

AI Usage: [Document any AI assistance used]

This is the main game file that ties all modules together.
Demonstrates module integration and complete game flow.
"""

# Import all our custom modules
import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data
from custom_exceptions import *

# ============================================================================
# GAME STATE
# ============================================================================

# Global variables for game data
current_character = None
all_quests = {}
all_items = {}
game_running = False

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    print("\n=== MAIN MENU ===")
    print("1. New Game")
    print("2. Load Game")
    print("3. Exit")

    while True:
        choice = input("Choose (1-3): ").strip()
        if choice in ("1", "2", "3"):
            return int(choice)
        print("Please enter 1, 2, or 3.")

def new_game():
    global current_character
    print("\n=== NEW GAME ===")
    name = input("Enter character name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    print("Choose class: Warrior, Mage, Rogue, Cleric")
    cls = input("Class: ").strip().title()

    try:
        char = character_manager.create_character(name, cls)
    except InvalidCharacterClassError as e:
        print(f"Invalid class: {e}")
        return

    try:
        character_manager.save_character(char)
    except Exception as e:
        print(f"Warning: could not auto-save character: {e}")

    current_character = char
    print(f"Welcome, {char['name']} the {char['class']}!")
    game_loop()

def load_game():
    global current_character
    print("\n=== LOAD GAME ===")

    saves = character_manager.list_saved_characters()
    if not saves:
        print("No saved characters found.")
        return

    print("Saved characters:")
    for i, name in enumerate(saves, start=1):
        print(f"{i}. {name}")

    while True:
        choice = input(f"Select (1-{len(saves)}) or 'c' to cancel: ").strip()
        if choice.lower() == 'c':
            return
        if choice.isdigit() and 1 <= int(choice) <= len(saves):
            sel = saves[int(choice) - 1]
            try:
                char = character_manager.load_character(sel)
                current_character = char
                print(f"Loaded {char['name']} the {char['class']}.")
                game_loop()
                return
            except CharacterNotFoundError:
                print("Save not found.")
                return
            except SaveFileCorruptedError:
                print("Save file appears corrupted.")
                return
            except InvalidSaveDataError as e:
                print(f"Invalid save data: {e}")
                return
        print("Invalid selection.")

# ============================================================================
# GAME LOOP
# ============================================================================

def game_loop():
    global game_running, current_character
    
    game_running = True
    
    while game_running:
        if current_character is None:
            print("No active character. Returning to main menu.")
            return

        choice = game_menu()

        if choice == 1:
            view_character_stats()
        elif choice == 2:
            view_inventory()
        elif choice == 3:
            quest_menu()
        elif choice == 4:
            explore()
            if current_character is None:
                return
        elif choice == 5:
            shop()
        elif choice == 6:
            save_game()
            print("Saved. Returning to main menu.")
            return
        else:
            print("Invalid selection.")

        try:
            save_game()
        except Exception as e:
            print(f"Auto-save failed: {e}")

def game_menu():
    print("\n=== GAME MENU ===")
    print("1. View Character Stats")
    print("2. View Inventory")
    print("3. Quest Menu")
    print("4. Explore (Find Battles)")
    print("5. Shop")
    print("6. Save and Quit")

    while True:
        choice = input("Choose (1-6): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= 6:
            return int(choice)
        print("Please enter a number from 1 to 6.")

# ============================================================================
# GAME ACTIONS
# ============================================================================

def view_character_stats():
    global current_character
    c = current_character
    if c is None:
        print("No character loaded.")
        return

    print("\n=== CHARACTER STATS ===")
    print(f"Name: {c['name']}")
    print(f"Class: {c['class']}")
    print(f"Level: {c['level']}  XP: {c['experience']}")
    print(f"HP: {c['health']}/{c['max_health']}")
    print(f"STR: {c['strength']}  MAG: {c['magic']}")
    print(f"Gold: {c['gold']}")
    print(f"Inventory slots: {len(c['inventory'])}/{inventory_system.MAX_INVENTORY_SIZE}")
    total_quests = len(all_quests)
    completed = len(c['completed_quests'])
    active = len(c['active_quests'])
    print(f"Quests: {active} active, {completed} completed ({total_quests} total)")

def view_inventory():
    global current_character, all_items
    
    c = current_character
    if c is None:
        print("No character loaded.")
        return

    while True:
        print("\n=== INVENTORY ===")
        inventory_system.display_inventory(c, all_items)
        print("\nOptions: ")
        print("1. Use item")
        print("2. Equip weapon")
        print("3. Equip armor")
        print("4. Unequip weapon")
        print("5. Unequip armor")
        print("6. Drop item")
        print("7. Back")

        choice = input("Choose (1-7): ").strip()

        # 1 — Use item
        if choice == "1":
            item_id = input("Enter item id to use: ").strip()
            if item_id not in all_items:
                print("Item not found in item list.")
                continue
            item_data = all_items[item_id]

            try:
                result = inventory_system.use_item(c, item_id, item_data)
                print(result)
            except ItemNotFoundError:
                print("Item not found in inventory.")
            except InvalidItemTypeError:
                print("That item cannot be used.")
            except Exception as e:
                print(f"Error using item: {e}")

        # 2 — Equip weapon
        elif choice == "2":
            item_id = input("Enter weapon id to equip: ").strip()
            if item_id not in all_items:
                print("Item not found.")
                continue
            item_data = all_items[item_id]

            try:
                print(inventory_system.equip_weapon(c, item_id, item_data))
            except ItemNotFoundError:
                print("Item not found in inventory.")
            except InvalidItemTypeError:
                print("Item is not a weapon.")
            except InventoryFullError:
                print("No space to unequip current weapon.")
            except Exception as e:
                print(f"Error equipping weapon: {e}")

        # 3 — Equip armor
        elif choice == "3":
            item_id = input("Enter armor id to equip: ").strip()
            if item_id not in all_items:
                print("Item not found.")
                continue
            item_data = all_items[item_id]

            try:
                print(inventory_system.equip_armor(c, item_id, item_data))
            except ItemNotFoundError:
                print("Item not found in inventory.")
            except InvalidItemTypeError:
                print("Item is not armor.")
            except InventoryFullError:
                print("No space to unequip current armor.")
            except Exception as e:
                print(f"Error equipping armor: {e}")

        # 4 — Unequip weapon
        elif choice == "4":
            try:
                item = inventory_system.unequip_weapon(c)
                if item:
                    print(f"Unequipped {item}.")
                else:
                    print("No weapon equipped.")
            except InventoryFullError:
                print("No inventory space to unequip weapon.")

        # 5 — Unequip armor
        elif choice == "5":
            try:
                item = inventory_system.unequip_armor(c)
                if item:
                    print(f"Unequipped {item}.")
                else:
                    print("No armor equipped.")
            except InventoryFullError:
                print("No inventory space to unequip armor.")

        # 6 — Drop item
        elif choice == "6":
            item_id = input("Enter item id to drop: ").strip()
            try:
                inventory_system.remove_item_from_inventory(c, item_id)
                print(f"Dropped {item_id}.")
            except ItemNotFoundError:
                print("Item not found in inventory.")
            except Exception as e:
                print(f"Error dropping item: {e}")

        # 7 — Back
        elif choice == "7":
            return
        else:
            print("Invalid option.")

def quest_menu():
    global current_character, all_quests
    c = current_character
    if c is None:
        print("No character loaded.")
        return

    while True:
        print("\n=== QUEST MENU ===")
        print("1. View Active Quests")
        print("2. View Available Quests")
        print("3. View Completed Quests")
        print("4. Accept Quest")
        print("5. Abandon Quest")
        print("6. Complete Quest (test)")
        print("7. Back")

        choice = input("Choose (1-7): ").strip()

        if choice == "1":
            active = quest_handler.get_active_quests(c, all_quests)
            if not active:
                print("No active quests.")
            else:
                for q in active:
                    quest_handler.display_quest_info(q)

        elif choice == "2":
            available = quest_handler.get_available_quests(c, all_quests)
            if not available:
                print("No available quests.")
            else:
                for q in available:
                    quest_handler.display_quest_info(q)

        elif choice == "3":
            completed = quest_handler.get_completed_quests(c, all_quests)
            if not completed:
                print("No completed quests.")
            else:
                for q in completed:
                    quest_handler.display_quest_info(q)

        elif choice == "4":
            quest_id = input("Enter quest id to accept: ").strip()
            try:
                quest_handler.accept_quest(c, quest_id, all_quests)
                print("Quest accepted.")
            except QuestNotFoundError:
                print("Quest not found.")
            except InsufficientLevelError:
                print("Your level is too low.")
            except QuestRequirementsNotMetError:
                print("Quest prerequisites not met.")
            except QuestAlreadyCompletedError:
                print("Quest already completed.")
            except Exception as e:
                print(f"Error accepting quest: {e}")

        elif choice == "5":
            quest_id = input("Enter quest id to abandon: ").strip()
            try:
                quest_handler.abandon_quest(c, quest_id)
                print("Quest abandoned.")
            except QuestNotActiveError:
                print("That quest is not active.")
            except Exception as e:
                print(f"Error abandoning quest: {e}")

        elif choice == "6":
            quest_id = input("Enter quest id to complete: ").strip()
            try:
                rewards = quest_handler.complete_quest(c, quest_id, all_quests)
                print(f"Quest completed! +{rewards['reward_xp']} XP, +{rewards['reward_gold']} gold.")
            except QuestNotFoundError:
                print("Quest not found.")
            except QuestNotActiveError:
                print("Quest is not active.")
            except Exception as e:
                print(f"Error completing quest: {e}")

        elif choice == "7":
            return
        else:
            print("Invalid option.")

def explore():
    global current_character
    
    c = current_character
    if c is None:
        print("No character loaded.")
        return

    print("\nYou explore the wilds...")
    enemy = combat_system.get_random_enemy_for_level(c['level'])
    battle = combat_system.SimpleBattle(c, enemy)

    try:
        result = battle.start_battle()
    except CharacterDeadError:
        print("You are dead and cannot fight.")
        return

    # Removed .get()
    if "winner" in result and result["winner"] == "player":

        if "xp" not in result:
            xp = 0
        else:
            xp = result["xp"]

        if "gold" not in result:
            gold = 0
        else:
            gold = result["gold"]

        try:
            character_manager.gain_experience(c, xp)
        except CharacterDeadError:
            print("Error: character dead while awarding XP.")

        try:
            character_manager.add_gold(c, gold)
        except ValueError:
            print("Error adding gold.")

        print(f"You gained {xp} XP and {gold} gold!")

    else:
        print("You were defeated.")
        handle_character_death()

def shop():
    global current_character, all_items
    
    c = current_character
    if c is None:
        print("No character loaded.")
        return

    item_keys = list(all_items.keys())
    while True:
        print("\n=== SHOP ===")
        print(f"Gold: {c['gold']}")
        for i, key in enumerate(item_keys, start=1):
            itm = all_items[key]
            print(f"{i}. {itm['name']} ({key}) - {itm['type']} - Cost: {itm['cost']}")
        print(f"{len(item_keys)+1}. Sell item")
        print(f"{len(item_keys)+2}. Back")

        choice = input(f"Choose (1-{len(item_keys)+2}): ").strip()
        if not choice.isdigit():
            print("Enter a number.")
            continue
        choice = int(choice)

        # Buy
        if 1 <= choice <= len(item_keys):
            item_id = item_keys[choice - 1]
            item_data = all_items[item_id]
            try:
                inventory_system.purchase_item(c, item_id, item_data)
                print(f"Purchased {item_data['name']}.")
            except InsufficientResourcesError:
                print("Not enough gold.")
            except InventoryFullError:
                print("Inventory is full.")
            except Exception as e:
                print(f"Error purchasing item: {e}")

        # Sell
        elif choice == len(item_keys) + 1:
            sid = input("Enter item id to sell: ").strip()
            if sid not in c['inventory']:
                print("You don't have that item.")
                continue

            if sid not in all_items:
                print("Unknown item data; cannot sell.")
                continue

            item_data = all_items[sid]

            try:
                amt = inventory_system.sell_item(c, sid, item_data)
                print(f"Sold {sid} for {amt} gold.")
            except ItemNotFoundError:
                print("Item not found.")
            except Exception as e:
                print(f"Error selling item: {e}")

        # Back
        elif choice == len(item_keys) + 2:
            return
        else:
            print("Invalid choice.")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def save_game():
    global current_character
    
    if current_character is None:
        raise ValueError("No character to save.")
    try:
        character_manager.save_character(current_character)
        print("Game saved.")
    except PermissionError:
        print("Permission denied when saving game.")
    except IOError as e:
        print(f"I/O error when saving: {e}")
    except Exception as e:
        print(f"Unexpected save error: {e}")

def load_game_data():
    global all_quests, all_items
    
    try:
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()
    except MissingDataFileError:
        raise
    except InvalidDataFormatError as e:
        raise
    except CorruptedDataError as e:
        raise

def handle_character_death():
    global current_character, game_running
    
    c = current_character
    if c is None:
        return

    print("\n=== YOU HAVE FALLEN ===")
    print("1. Revive (cost: 50% of your current gold)")
    print("2. Quit to main menu (lose unsaved progress)")

    while True:
        choice = input("Choose (1-2): ").strip()
        if choice == "1":
            cost = max(1, c['gold'] // 2)
            if c['gold'] < cost:
                print("Not enough gold to revive.")
                continue
            try:
                character_manager.revive_character(c)
                try:
                    character_manager.add_gold(c, -cost)
                except ValueError:
                    pass
                print(f"You were revived for {cost} gold.")
            except Exception as e:
                print(f"Could not revive: {e}")
            return
        elif choice == "2":
            print("Quitting to main menu...")
            current_character = None
            game_running = False
            return
        else:
            print("Invalid option.")

def display_welcome():
    print("=" * 50)
    print("     QUEST CHRONICLES - A MODULAR RPG ADVENTURE")
    print("=" * 50)
    print("\nWelcome to Quest Chronicles!")
    print("Build your character, complete quests, and become a legend!")
    print()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    display_welcome()
    
    try:
        load_game_data()
        print("Game data loaded successfully!")
    except MissingDataFileError:
        print("Creating default game data...")
        game_data.create_default_data_files()
        load_game_data()
    except InvalidDataFormatError as e:
        print(f"Error loading game data: {e}")
        print("Please check data files for errors.")
        return
    
    while True:
        choice = main_menu()
        
        if choice == 1:
            new_game()
        elif choice == 2:
            load_game()
        elif choice == 3:
            print("\nThanks for playing Quest Chronicles!")
            break
        else:
            print("Invalid choice. Please select 1-3.")

if __name__ == "__main__":
    main()

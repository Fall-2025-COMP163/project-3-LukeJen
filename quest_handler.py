"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Starter Code

Name: [Luke Jensen]

AI Usage: [Bug Fixes]

This module handles quest management, dependencies, and completion.
"""

from custom_exceptions import (
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError
)


import character_manager

# ============================================================================
# QUEST MANAGEMENT
# ============================================================================

def accept_quest(character, quest_id, quest_data_dict):
    """
    Accept a new quest
    
    Args:
        character: Character dictionary
        quest_id: Quest to accept
        quest_data_dict: Dictionary of all quest data
    
    Requirements to accept quest:
    - Character level >= quest required_level
    - Prerequisite quest completed (if any)
    - Quest not already completed
    - Quest not already active
    
    Returns: True if quest accepted
    Raises:
        QuestNotFoundError if quest_id not in quest_data_dict
        InsufficientLevelError if character level too low
        QuestRequirementsNotMetError if prerequisite not completed
        QuestAlreadyCompletedError if quest already done
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")

    quest = quest_data_dict[quest_id]

    # Level requirement
    if character['level'] < quest['required_level']:
        raise InsufficientLevelError("Character level is too low.")

    # Prerequisite check
    prereq = quest['prerequisite']
    if prereq != "NONE" and prereq not in character['completed_quests']:
        raise QuestRequirementsNotMetError("Prerequisite quest not completed.")

    # Not already completed
    if quest_id in character['completed_quests']:
        raise QuestAlreadyCompletedError("Quest already completed.")

    # Not already active
    if quest_id in character['active_quests']:
        raise QuestRequirementsNotMetError("Quest already active.")

    # Accept quest
    character['active_quests'].append(quest_id)
    return True

def complete_quest(character, quest_id, quest_data_dict):
    """
    Complete an active quest and grant rewards
    
    Args:
        character: Character dictionary
        quest_id: Quest to complete
        quest_data_dict: Dictionary of all quest data
    
    Rewards:
    - Experience points (reward_xp)
    - Gold (reward_gold)
    
    Returns: Dictionary with reward information
    Raises:
        QuestNotFoundError if quest_id not in quest_data_dict
        QuestNotActiveError if quest not in active_quests
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")

    if quest_id not in character['active_quests']:
        raise QuestNotActiveError("Cannot complete a quest that is not active.")

    quest = quest_data_dict[quest_id]

    # Remove from active, add to completed
    character['active_quests'].remove(quest_id)
    character['completed_quests'].append(quest_id)

    # Grant rewards
    xp = quest['reward_xp']
    gold = quest['reward_gold']

    character_manager.gain_experience(character, xp)
    character_manager.add_gold(character, gold)

    return {
        'reward_xp': xp,
        'reward_gold': gold
    }

def abandon_quest(character, quest_id):
    """
    Remove a quest from active quests without completing it
    
    Returns: True if abandoned
    Raises: QuestNotActiveError if quest not active
    """
    if quest_id not in character['active_quests']:
        raise QuestNotActiveError("Quest is not active.")

    character['active_quests'].remove(quest_id)
    return True

def get_active_quests(character, quest_data_dict):
    """
    Get full data for all active quests
    
    Returns: List of quest dictionaries for active quests
    """
    return [quest_data_dict[q] for q in character['active_quests']]

def get_completed_quests(character, quest_data_dict):
    """
    Get full data for all completed quests
    
    Returns: List of quest dictionaries for completed quests
    """
    return [quest_data_dict[q] for q in character['completed_quests']]

def get_available_quests(character, quest_data_dict):
    """
    Get quests that character can currently accept
    
    Available = meets level req + prerequisite done + not completed + not active
    
    Returns: List of quest dictionaries
    """
    available = []

    for q_id, q_data in quest_data_dict.items():
        if can_accept_quest(character, q_id, quest_data_dict):
            available.append(q_data)

    return available

# ============================================================================
# QUEST TRACKING
# ============================================================================

def is_quest_completed(character, quest_id):
    """
    Check if a specific quest has been completed
    
    Returns: True if completed, False otherwise
    """
    return quest_id in character['completed_quests']

def is_quest_active(character, quest_id):
    """
    Check if a specific quest is currently active
    
    Returns: True if active, False otherwise
    """
    return quest_id in character['active_quests']

def can_accept_quest(character, quest_id, quest_data_dict):
    """
    Check if character meets all requirements to accept quest
    
    Returns: True if can accept, False otherwise
    Does NOT raise exceptions - just returns boolean
    """
    if quest_id not in quest_data_dict:
        return False

    quest = quest_data_dict[quest_id]

    if character['level'] < quest['required_level']:
        return False

    prereq = quest['prerequisite']
    if prereq != "NONE" and prereq not in character['completed_quests']:
        return False

    if quest_id in character['completed_quests']:
        return False

    if quest_id in character['active_quests']:
        return False

    return True

def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    """
    Get the full chain of prerequisites for a quest
    
    Returns: List of quest IDs in order [earliest_prereq, ..., quest_id]
    Example: If Quest C requires Quest B, which requires Quest A:
             Returns ["quest_a", "quest_b", "quest_c"]
    
    Raises: QuestNotFoundError if quest doesn't exist
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")

    chain = []
    current = quest_id

    while current != "NONE":
        if current not in quest_data_dict:
            raise QuestNotFoundError(f"Prerequisite '{current}' not found.")

        chain.append(current)
        current = quest_data_dict[current]['prerequisite']

    return chain[::-1]

# ============================================================================
# QUEST STATISTICS
# ============================================================================

def get_quest_completion_percentage(character, quest_data_dict):
    """
    Calculate what percentage of all quests have been completed
    
    Returns: Float between 0 and 100
    """
    total = len(quest_data_dict)
    completed = len(character['completed_quests'])
    if total == 0:
        return 0.0
    return (completed / total) * 100

def get_total_quest_rewards_earned(character, quest_data_dict):
    """
    Calculate total XP and gold earned from completed quests
    
    Returns: Dictionary with 'total_xp' and 'total_gold'
    """
    total_xp = 0
    total_gold = 0

    for q_id in character['completed_quests']:
        quest = quest_data_dict[q_id]
        total_xp += quest['reward_xp']
        total_gold += quest['reward_gold']

    return {
        'total_xp': total_xp,
        'total_gold': total_gold
    }

def get_quests_by_level(quest_data_dict, min_level, max_level):
    """
    Get all quests within a level range
    
    Returns: List of quest dictionaries
    """
    return [
        q_data for q_data in quest_data_dict.values()
        if min_level <= q_data['required_level'] <= max_level
    ]

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_quest_info(quest_data):
    """
    Display formatted quest information
    
    Shows: Title, Description, Rewards, Requirements
    """
    print(f"\n=== {quest_data['title']} ===")
    print(f"Description: {quest_data['description']}")
    print(f"Required Level: {quest_data['required_level']}")
    print(f"Prerequisite: {quest_data['prerequisite']}")
    print(f"Rewards → XP: {quest_data['reward_xp']}, Gold: {quest_data['reward_gold']}")

def display_quest_list(quest_list):
    """
    Display a list of quests in summary format
    
    Shows: Title, Required Level, Rewards
    """
    print("\n--- Quest List ---")
    for q in quest_list:
        print(f"{q['title']} (Lvl {q['required_level']}) - XP: {q['reward_xp']} | Gold: {q['reward_gold']}")

def display_character_quest_progress(character, quest_data_dict):
    """
    Display character's quest statistics and progress
    
    Shows:
    - Active quests count
    - Completed quests count
    - Completion percentage
    - Total rewards earned
    """
    print("\n=== QUEST PROGRESS ===")
    print(f"Active Quests: {len(character['active_quests'])}")
    print(f"Completed Quests: {len(character['completed_quests'])}")
    print(f"Completion: {get_quest_completion_percentage(character, quest_data_dict):.2f}%")

    rewards = get_total_quest_rewards_earned(character, quest_data_dict)
    print(f"Total XP Earned: {rewards['total_xp']}")
    print(f"Total Gold Earned: {rewards['total_gold']}")

# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_prerequisites(quest_data_dict):
    """
    Validate that all quest prerequisites exist
    
    Checks that every prerequisite (that's not "NONE") refers to a real quest
    
    Returns: True if all valid
    Raises: QuestNotFoundError if invalid prerequisite found
    """
    for q_id, q_data in quest_data_dict.items():
        prereq = q_data['prerequisite']
        if prereq != "NONE" and prereq not in quest_data_dict:
            raise QuestNotFoundError(f"Quest '{q_id}' has invalid prerequisite '{prereq}'.")
    return True


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== QUEST HANDLER TEST ===")
    
    # Test data
    # test_char = {
    #     'level': 1,
    #     'active_quests': [],
    #     'completed_quests': [],
    #     'experience': 0,
    #     'gold': 100
    # }
    #
    # test_quests = {
    #     'first_quest': {
    #         'quest_id': 'first_quest',
    #         'title': 'First Steps',
    #         'description': 'Complete your first quest',
    #         'reward_xp': 50,
    #         'reward_gold': 25,
    #         'required_level': 1,
    #         'prerequisite': 'NONE'
    #     }
    # }
    #
    # try:
    #     accept_quest(test_char, 'first_quest', test_quests)
    #     print("Quest accepted!")
    # except QuestRequirementsNotMetError as e:
    #     print(f"Cannot accept: {e}")


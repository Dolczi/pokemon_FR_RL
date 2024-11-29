from pyboy.utils import bcd_to_dec
# Memory adresses
PARTY_SIZE_ADDRES = 0xD163
BADGES_COUNT_ADDRES = 0xD356
PARTY_ID_ADDRESSES = [0xD164, 0xD165, 0xD166, 0xD167, 0xD168, 0xD169]
PARTY_TYPES_ADDRESSES = [
                0xD170,
                0xD171,
                0xD19C,
                0xD19D,
                0xD1C8,
                0xD1C9,
                0xD1F4,
                0xD1F5,
                0xD220,
                0xD221,
                0xD24C,
                0xD24D,
            ]
PARTY_LEVEL_ADDRESSES = [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268]
PARTY_STATUS_ADDRESSES = [0xD16F, 0xD19B, 0xD1C7, 0xD1F3, 0xD21F, 0xD24B]
PARTY_HP_ADDRESSES = [0xD16C, 0xD198, 0xD1C4, 0xD1F0, 0xD21C, 0xD248]
PARTY_MAX_HP_ADDRESSES = [0xD18D, 0xD1B9, 0xD1E5, 0xD211, 0xD23D, 0xD269]
PARTY_EXP_ADDRESSES = [0xD179, 0xD1A5, 0xD1D1, 0xD1FD, 0xD229, 0xD255]
MONEY_ADDRESSES = [0xD347, 0xD348, 0xD349]
CURRENT_MAP_ADDRESS = 0xD35E
X_POS_ADDRESS = 0xD362
Y_POS_ADDRESS = 0xD361

# Add learning settings

# Read memory functions

def read_money(pyboy):
    return (
         bcd_to_dec(pyboy.memory[MONEY_ADDRESSES[2]]) + 
         bcd_to_dec(pyboy.memory[MONEY_ADDRESSES[1]]) * 100 + 
         bcd_to_dec(pyboy.memory[MONEY_ADDRESSES[0]]) * 10000
         )

def read_levels(pyboy):
    return [pyboy.memory[a] for a in PARTY_LEVEL_ADDRESSES]

def read_party_id(pyboy):
    return [pyboy.memory[a] for a in PARTY_ID_ADDRESSES]

def read_party_hp(pyboy):
    return [256*pyboy.memory[a] + pyboy.memory[a+1] for a in PARTY_HP_ADDRESSES]

def read_party_max_hp(pyboy):
    return [256*pyboy.memory[a] + pyboy.memory[a+1] for a in PARTY_MAX_HP_ADDRESSES]

def read_party_exp(pyboy):
    return [pyboy.memory[a] for a in PARTY_EXP_ADDRESSES]

def read_party_status(pyboy):
    return [pyboy.memory[a] for a in PARTY_STATUS_ADDRESSES]

def read_party_types(pyboy):
    return [pyboy.memory[a] for a in PARTY_TYPES_ADDRESSES]

def read_number_of_badges(pyboy):
    return int(pyboy.memory[BADGES_COUNT_ADDRES]).bit_count()

def read_party_size(pyboy):
    return pyboy.memory[PARTY_SIZE_ADDRES]

def read_location(pyboy):
    return (pyboy.memory[CURRENT_MAP_ADDRESS], pyboy.memory[X_POS_ADDRESS], pyboy.memory[Y_POS_ADDRESS])

# Rewards

def get_location_reward(pyboy, agent_explored):
    current_location = read_location(pyboy)
    if current_location not in agent_explored:
        return 1
    return 0

def get_levels_reward(pyboy, current_agent_stats):
    current_levels = sum(read_levels(pyboy))
    if current_levels > current_agent_stats['levels']:
        return current_levels - current_agent_stats['levels']
    return 0

# Health increases and player didn't die, new pokemon wasn't catched
def get_healing_reward(pyboy, current_agent_stats):
    current_health = sum(read_party_hp(pyboy))/sum(read_party_max_hp(pyboy))
    current_party_size = read_party_size(pyboy)
    if current_health > current_agent_stats['health'] and current_party_size == current_party_size['party_size'] and current_agent_stats['health'] != 0:
        return current_health - current_agent_stats['health']
    return 0

# Won trainer battle
def get_trainer_battle_reward(pyboy, current_agent_stats):
    if read_money(pyboy) > current_agent_stats['money']:
        return 1
    return 0

# Won new badge
def get_badges_reward(pyboy, current_agent_stats):
    if read_number_of_badges(pyboy) > current_agent_stats['badges']:
        return 1
    return 0

def calculate_reward(pyboy, agent_explored, current_agent_stats):
        rewards = {
            'exploration': get_location_reward(pyboy, agent_explored, current_agent_stats) * 0.05,
            'levels': get_levels_reward(pyboy, current_agent_stats),
            'trainer_battles': get_trainer_battle_reward(pyboy, current_agent_stats) * 3,
            'healing': get_healing_reward(pyboy, current_agent_stats) * 4,
            'badges': get_badges_reward(pyboy, current_agent_stats) * 5
        }
        reward = sum([key for key in rewards])
        return reward

def get_agent_stats(pyboy):
    stats = {
        'location': read_location(pyboy),
        'levels': sum(read_levels(pyboy)),
        'health': sum(read_party_hp(pyboy))/sum(read_party_max_hp(pyboy)),
        'money': read_money(pyboy),
        'badges': read_number_of_badges(pyboy),
        'party_size': read_party_size(pyboy)
    }
    return stats

def update_explored(agent_explored, agent_current_stats):
    if agent_current_stats['location'] not in agent_explored:
        agent_explored.append(agent_current_stats['location'])
        return agent_explored
    return agent_explored

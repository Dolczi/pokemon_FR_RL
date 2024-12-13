from pyboy.utils import bcd_to_dec
import numpy as np
from skimage.transform import resize
import matplotlib.pyplot as plt
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
IS_IN_BATTLE_ADDRESS = 0xD057
WILD_POKEMON_HP = 0xCFE7

############################################################################################################################
def get_observation(pyboy, recent_screens, recent_actions, output_shape):
    recent_screens = np.roll(recent_screens, 1, axis=2)
    recent_screens[:,:,0] = get_screen_downscaled(pyboy, output_shape)
    observation = {
                'screen': recent_screens,
                'location': np.array(read_location(pyboy)),
                'hp': np.array([sum(read_party_hp(pyboy))/sum(read_party_max_hp(pyboy))]),
                'level': np.array([sum(read_levels(pyboy))]),
                'badges': np.array([read_number_of_badges(pyboy)]),
                'recent_actions': recent_actions,
                'is_in_battle': np.array([read_in_battle(pyboy)])
                }
    return observation, recent_screens

def get_screen_downscaled(pyboy, output_shape):
    pixels = pyboy.screen.ndarray[:,:,0:1]
    downscaled_pixels = resize(
        pixels,
        output_shape=output_shape,
        anti_aliasing=True,  
        preserve_range=True
    ).astype(np.uint8)
    #plt.imshow(downscaled_pixels[:,:,0], cmap="gray")
    #plt.show()
    return downscaled_pixels[:,:,0]

def read_location(pyboy):
    return (pyboy.memory[CURRENT_MAP_ADDRESS], pyboy.memory[X_POS_ADDRESS], pyboy.memory[Y_POS_ADDRESS])

def read_party_hp(pyboy):
    return [256*pyboy.memory[i] + pyboy.memory[i+1] for i in PARTY_HP_ADDRESSES]

def read_party_max_hp(pyboy):
    return [256*pyboy.memory[i] + pyboy.memory[i+1] for i in PARTY_MAX_HP_ADDRESSES]

def read_levels(pyboy):
    return [pyboy.memory[i] for i in PARTY_LEVEL_ADDRESSES]

def read_number_of_badges(pyboy):
    return int(pyboy.memory[BADGES_COUNT_ADDRES]).bit_count()

def read_in_battle(pyboy):
    return pyboy.memory[IS_IN_BATTLE_ADDRESS]

def get_agent_stats(pyboy):
    stats = {
        'location': read_location(pyboy),
        'hp': sum(read_party_hp(pyboy))/sum(read_party_max_hp(pyboy)),
        'level': sum(read_levels(pyboy)),
        'money': read_money(pyboy),
        'badges': read_number_of_badges(pyboy),
        'party_size': read_party_size(pyboy),
        'in_battle': read_in_battle(pyboy),
        'enemy_hp': read_enemy_hp(pyboy)
    }
    return stats

def read_party_size(pyboy):
    return pyboy.memory[PARTY_SIZE_ADDRES]

def read_money(pyboy):
    return (
         bcd_to_dec(pyboy.memory[MONEY_ADDRESSES[2]]) + 
         bcd_to_dec(pyboy.memory[MONEY_ADDRESSES[1]]) * 100 + 
         bcd_to_dec(pyboy.memory[MONEY_ADDRESSES[0]]) * 10000
         )

def read_enemy_hp(pyboy):
    return pyboy.memory[WILD_POKEMON_HP]

def update_explored(agent_explored, agent_current_stats):
    if agent_current_stats['location'] in agent_explored and agent_current_stats['in_battle'] != 0:
        agent_explored[agent_current_stats['location']] += 1
    else:
        agent_explored[agent_current_stats['location']] = 1
    return agent_explored

def update_max_level(agent_max_level, agent_current_stats):
    return max(agent_max_level, agent_current_stats['level'])

def calculate_reward(agent_explored, agent_current_stats, agent_stats, step_count, agent_max_level):
    reward_dict = {
        'exploration': get_exploration_reward(agent_current_stats, agent_explored) * 0.1,
        'level': get_levels_reward(agent_current_stats, agent_max_level),
        'healing': get_healing_reward(agent_current_stats, agent_stats, step_count) * 10,
        'battle': get_battle_reward(agent_current_stats, agent_stats, step_count) * 3,
        'gym_battle': get_gym_battle_reward(agent_current_stats, agent_stats, step_count) * 10,
        'blocked': get_stuck_reward(agent_explored, agent_current_stats) * -0.5
    }
    reward = 0
    for i in reward_dict.values():
        reward += i
    return reward

def get_exploration_reward(agent_current_stats, agent_explored):
    if agent_current_stats['location'] not in agent_explored:
        return 1
    return 0

def get_levels_reward(agent_current_stats, agent_max_level):
    if agent_current_stats['level'] > agent_max_level:
        return agent_current_stats['level'] - agent_max_level
    return 0

def get_healing_reward(agent_current_stats, agent_stats, step_count):
    if agent_current_stats['hp'] > agent_stats[step_count]['hp'] and agent_stats[step_count]['hp'] != 0:
        return agent_current_stats['hp'] - agent_stats[step_count]['hp']
    return 0

def get_battle_reward(agent_current_stats, agent_stats, step_count):
    if agent_current_stats['in_battle'] < agent_stats[step_count]['in_battle'] and agent_current_stats['enemy_hp'] < agent_stats[step_count]['enemy_hp']:
        return 1
    return 0

def get_gym_battle_reward(agent_current_stats, agent_stats, step_count):
    if agent_current_stats['badges'] > agent_stats[step_count]['badges']:
        return 1
    return 0

def get_stuck_reward(agent_explored, agent_current_stats):
    if agent_current_stats['location'] in agent_explored and agent_explored[agent_current_stats['location']] > 200:
        return 1
    return 0
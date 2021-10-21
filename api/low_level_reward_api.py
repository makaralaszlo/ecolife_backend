from flask import Blueprint, request
from objects.reward import Reward
from database.database import DataBase
from config.api_config import BASE_URI


low_api_reward = Blueprint(name='low_level_reward_api', import_name=__name__)
reward_db = DataBase('EcoLife', 'reward')


@low_api_reward.route(f'{BASE_URI}/create_reward', methods=['POST'])
def create_reward():
    pass


@low_api_reward.route(f'{BASE_URI}/get_reward', methods=['GET'])
def get_reward():
    pass


@low_api_reward.route(f'{BASE_URI}/delete_reward', methods=['POST'])
def delete_reward():
    pass

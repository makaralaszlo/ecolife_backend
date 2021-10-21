from flask import Blueprint, request
from database.database import DataBase
from objects.task import Task
from objects.reward import Reward
from objects.submit import Submit
from objects.admin_profile import AdminProfile
from objects.user_profile import UserProfile
import json
import typing

low_api = Blueprint(name='low_level_api', import_name=__name__)
BASE_URI = '/api/v1'

user_db = DataBase('EcoLife', 'user')
admin_db = DataBase('EcoLife', 'admin')
task_db = DataBase('EcoLife', 'task')
reward_db = DataBase('EcoLife', 'reward')
submit_db = DataBase('EcoLife', 'submit')


@low_api.route(f'{BASE_URI}/create_profile', methods=['POST'])
def create_profile():
    """
    Payload kinézete AdminProfile esetén:
    {
        'type': 'AdminProfile',
        'data': {
                 '_id': str,
                 'email_address': str,
                 'first_name': str,
                 'last_name': str,
                 'date_of_birth': str,
                 'password': str,
                 'company': str,
                 'rewards': list,
                 'tasks': list
                }
    }
    Payload kinézete UserProfile esetén:
    {
        'type': 'UserProfile',
        'data': {
                 '_id': str,
                 'email_address': str,
                 'first_name': str,
                 'last_name': str,
                 'date_of_birth': str,
                 'password': str,
                 'rewards': list,
                 'tasks': list
                }
    }

    Hiba visszatérés rossz type megadása esetén:
    {
        'type': 'Error',
        'data': {
                 'description': 'Incorrect type passed'
                }
    }
    Sikeres végig futás esetén:
    {
        'type': 'Success',
        'data': {
                 'description': '61715db40b13ec7cc2387db6'
                }
    }

    :return:
    """
    req_data = request.json
    if req_data['type'] == 'AdminProfile':
        admin_profile = AdminProfile(
            _id=req_data['data']['_id'] if '_id' in req_data['data'] else 'null',
            email_address=req_data['data']['email_address'],
            first_name=req_data['data']['first_name'],
            last_name=req_data['data']['last_name'],
            date_of_birth=req_data['data']['date_of_birth'],
            password=req_data['data']['password'],
            company=req_data['data']['company'],
            rewards=req_data['data']['rewards'],
            tasks=req_data['data']['tasks']
        )

        db_resp, success = admin_db.insert_element(
            search_data_dict={'email_address': req_data['data']['email_address']},
            insert_data_dict=admin_profile.to_dict())

        if not success:
            ret_data = {
                'type': 'Error',
                'data': {
                    'description': db_resp
                }
            }
        else:
            ret_data = {
                'type': 'Success',
                'data': {
                    'description': db_resp
                }
            }

    elif req_data['type'] == 'UserProfile':
        user_profile = UserProfile(
            _id=req_data['data']['_id'] if '_id' in req_data['data'] else 'null',
            email_address=req_data['data']['email_address'],
            first_name=req_data['data']['first_name'],
            last_name=req_data['data']['last_name'],
            date_of_birth=req_data['data']['date_of_birth'],
            password=req_data['data']['password'],
            rewards=req_data['data']['rewards'],
            tasks=req_data['data']['tasks']
        )

        db_resp, success = user_db.insert_element(
            search_data_dict={'email_address': req_data['data']['email_address']},
            insert_data_dict=user_profile.to_dict())

        if not success:
            ret_data = {
                'type': 'Error',
                'data': {
                    'description': db_resp
                }
            }
        else:
            ret_data = {
                'type': 'Success',
                'data': {
                    'description': db_resp
                }
            }
    else:
        ret_data = {
            'type': 'Error',
            'data': {
                'description': 'Incorrect type passed'
            }
        }

    return json.dumps(ret_data)


@low_api.route(f'{BASE_URI}/get_profile', methods=['GET'])
def get_profile():
    return ' FASZ '


@low_api.route(f'{BASE_URI}/delete_profile', methods=['POST'])
def delete_profile():
    pass


@low_api.route(f'{BASE_URI}/create_reward', methods=['POST'])
def create_reward():
    pass


@low_api.route(f'{BASE_URI}/get_reward', methods=['GET'])
def get_reward():
    pass


@low_api.route(f'{BASE_URI}/delete_reward', methods=['POST'])
def delete_reward():
    pass


@low_api.route(f'{BASE_URI}/create_task', methods=['POST'])
def create_task():
    pass


@low_api.route(f'{BASE_URI}/get_task', methods=['GET'])
def get_task():
    pass


@low_api.route(f'{BASE_URI}/delete_task', methods=['POST'])
def delete_task():
    pass


@low_api.route(f'{BASE_URI}/create_submit', methods=['POST'])
def create_submit():
    pass


@low_api.route(f'{BASE_URI}/get_submit', methods=['GET'])
def get_submit():
    pass


@low_api.route(f'{BASE_URI}/delete_submit', methods=['POST'])
def delete_submit():
    pass


@low_api.route(f'{BASE_URI}/clear_database', methods=['POST'])
def clear_database():
    pass

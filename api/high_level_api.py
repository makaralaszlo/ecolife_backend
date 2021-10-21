from flask import Blueprint, request
from config.api_config import BASE_URI
import api.low_level_profile_api as low_level_profile_api
import json
import typing


high_api = Blueprint(name='high_level_api', import_name=__name__)


logged_in_users = {}


@high_api.route(f'{BASE_URI}/login', methods=['POST'])
def login_user():
    """
    Payload kinézete AdminProfile esetén e-mail és jelszó alapján:
    {
        'type': 'AdminProfile',
        'data': {
                'email_address': str,
                'password': str,
                }
    }

    Error kinézete:
    {
        'type': 'Error',
        'data': {
            'description': 'No profile assigned to these values!'
        }
    }

    :return:
    """
    global logged_in_users
    # felhasználó átadja az email és pw-t
    req_data = request.json

    if 'email_address' not in req_data['data'] and 'password' not in req_data['data']:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'Email address or Password not provided correctly!'
            }
        })

    profiles = low_level_profile_api.get_profile(req_data)

    if type(profiles) is str:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': profiles
            }
        })
    elif len(profiles) > 1:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'Internal server error! Multiple profiles with same e-mail assigned!'
            }
        })
    elif len(profiles) == 0:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'No profile assigned to these values!'
            }
        })

    profile_bearer_token = ''
    for profile_id, bearer_token in zip(logged_in_users.values(), logged_in_users.keys()):
        if profile_id == profiles[0].to_dict()['_id']:
            profile_bearer_token = bearer_token

    if profile_bearer_token == '':
        profile_bearer_token = profiles[0].get_bearer_token()
        logged_in_users[profile_bearer_token] = profiles[0].to_dict()['_id']

    return json.dumps({
        'type': 'Success',
        'data': {
            'description': profile_bearer_token
        }
    })


@high_api.route(f'{BASE_URI}/logout', methods=['POST'])
def logout_user():
    """
    Payload kinézete:
    {
        'type': 'UserProfile',
        'data': {}
    }

    :return:
    """
    global logged_in_users
    token = request.headers['Authorization'].split(' ')[-1]

    if token not in logged_in_users:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'User was not logged in!'
            }
        })

    del logged_in_users[token]
    return json.dumps({
        'type': 'Success',
        'data': {
            'description': 'User logged out!'
        }
    })


def register_user():
    pass


def get_mobile_main_screen():
    pass


def get_mobile_rewards_screen():
    pass


def get_mobile_tasks_screen():
    pass


def get_mobile_task_screen():
    # ez csak 1 darab task teljes nézeete
    pass


def get_admin_main_screen():
    pass


def get_admin_task_screen():
    pass

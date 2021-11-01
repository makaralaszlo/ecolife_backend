from flask import Blueprint, request
from config.api_config import BASE_URI
import api.low_level_profile_api as low_level_profile_api
import api.low_level_task_api as low_level_task_api
import json
import typing
from objects.admin_profile import AdminProfile
from objects.user_profile import UserProfile

high_api = Blueprint(name='high_level_api', import_name=__name__)

logged_in_users = {}
users = []


def get_profile_object(user_id: str) -> typing.Tuple[typing.Union[AdminProfile, UserProfile, str], bool]:
    global users
    for user in users:
        if user.get_id() == user_id:
            return user, True
    return 'Profile not loaded in correctly!', False


@high_api.route(f'{BASE_URI}/login', methods=['POST'])
def login_user() -> str:
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
    global users
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
    users += profiles

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
def logout_user() -> str:
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


@high_api.route(f'{BASE_URI}/tasks_mobile', methods=['GET'])
def get_mobile_tasks_screen() -> str:
    global logged_in_users
    try:
        token = request.headers['Authorization'].split(' ')[-1]
    except Exception as exp:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': str(exp)
            }
        })

    if token not in logged_in_users:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'User was not logged in!'
            }
        })

    profile, success = get_profile_object(logged_in_users[token])

    if not success:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': profile
            }
        })

    if type(profile) != UserProfile:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'Only Users can access these type of content!'
            }
        })

    resp = {
        'type': 'Success',
        'data': {
            'tasks': low_level_task_api.get_task({'_id': profile.get_id()})
        }
    }

    return json.dumps(resp)


@high_api.route(f'{BASE_URI}/main_screen', methods=['GET'])
def get_main_screen():
    # ha admin akkor az admin main screen függvényt kell meghvini
    # ha user akkor a user main screent kell meghivni
    pass


@high_api.route(f'{BASE_URI}/task_screen', methods=['GET'])
def get_task_screen():
    # ha admin akkor az admin task screen
    # ha user akkor a user main screent
    pass


def get_mobile_rewards_screen():
    pass


def get_mobile_task_screen():
    # ez csak 1 darab task teljes nézeete
    pass


def get_admin_main_screen():
    pass


def get_admin_task_screen():
    pass


def create_task():
    # admin csinál taskot
    pass

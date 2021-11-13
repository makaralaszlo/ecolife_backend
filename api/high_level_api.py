from flask import Blueprint, request
from config.api_config import BASE_URI
import api.low_level_profile_api as low_level_profile_api
import api.low_level_task_api as low_level_task_api
import api.low_level_reward_api as low_level_reward_api
import api.low_level_submit_api as low_level_submit_api
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


def check_profile_login(token) -> typing.Union[dict, typing.Tuple[UserProfile, bool]]:
    global logged_in_users

    if token not in logged_in_users:
        return {
            'type': 'Error',
            'data': {
                'description': 'User was not logged in!'
            }
        }

    profile, success = get_profile_object(logged_in_users[token])

    if not success:
        return {
            'type': 'Error',
            'data': {
                'description': profile
            }
        }

    return profile, success


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
            'description': low_level_task_api.get_task({'_id': profile.get_id()})
        }
    }

    return json.dumps(resp)


@high_api.route(f'{BASE_URI}/user_task_screen', methods=['GET'])
def get_user_task_screen():
    # ha user akkor a user main screent kell meghivni
    try:
        token = request.headers['Authorization'].split(' ')[-1]
    except Exception as exp:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': str(exp)
            }
        })

    resp = check_profile_login(token)
    if type(resp) == str:
        return json.dumps(resp)
    else:
        profile, success = resp

    if type(profile) != UserProfile:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'Only Users can access these type of content!'
            }
        })

    # taskokat kell visszadni ami csak a rövid név, valami available, accepted, declined
    available_tasks = []
    accepted_tasks = []
    rejected_tasks = []
    pending_tasks = []

    task_list = profile.to_dict()['tasks']

    for task in task_list:
        submit_resp, submit_success = low_level_submit_api.get_submit({
            'data': {
                'user_id': profile.get_id(),
                'task_id': task
            }
        })

        task_resp, task_success = low_level_task_api.get_task({
            'data': {
                '_id': task
            }
        })

        if submit_success and task_success:
            if str(submit_resp['data']['description'][0]['state']) == 'AVAILABLE':
                available_tasks.append({
                    'title': task_resp['data']['description'][0]['title'],
                    'company': task_resp['data']['description'][0]['company']
                })
            elif str(submit_resp['data']['description'][0]['state']) == 'ACCEPTED':
                accepted_tasks.append({
                    'title': task_resp['data']['description'][0]['title'],
                    'company': task_resp['data']['description'][0]['company']
                })
            elif str(submit_resp['data']['description'][0]['state']) == 'REJECTED':
                rejected_tasks.append({
                    'title': task_resp['data']['description'][0]['title'],
                    'company': task_resp['data']['description'][0]['company']
                })
            elif str(submit_resp['data']['description'][0]['state']) == 'PENDING':
                pending_tasks.append({
                    'title': task_resp['data']['description'][0]['title'],
                    'company': task_resp['data']['description'][0]['company']
                })

    return json.dumps({
        'type': 'Success',
        'data':
            {
                'description': {
                    'AVAILABLE': available_tasks,
                    'PENDING': pending_tasks,
                    'ACCEPTED': accepted_tasks,
                    'REJECTED': rejected_tasks
                }
            }
    })


@high_api.route(f'{BASE_URI}/user_profile_screen', methods=['GET'])
def get_mobile_profile_screen() -> str:
    # össze kell szedni a profild adatokat, kuponokat abből a kupon title és description
    try:
        token = request.headers['Authorization'].split(' ')[-1]
    except Exception as exp:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': str(exp)
            }
        })

    resp = check_profile_login(token)
    if type(resp) == str:
        return json.dumps(resp)
    else:
        profile, success = resp

    if type(profile) != UserProfile:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'Only Users can access these type of content!'
            }
        })

    profile_object = profile.to_dict()
    coupons = []

    coupon_list = profile.to_dict()['rewards']
    for coupon in coupon_list:
        reward_resp, reward_success = low_level_reward_api.get_reward({
            'data': {
                '_id': coupon
            }
        })

        coupons.append({
            '_id': str(reward_resp['data']['description'][0]['_id']),
            'title': reward_resp['data']['description'][0]['title'],
            'description': reward_resp['data']['description'][0]['description'],
            'company': reward_resp['data']['description'][0]['company'],
            'redeem_code': reward_resp['data']['description'][0]['redeem_code'],
            'expiration': reward_resp['data']['description'][0]['expiration']
        })

    return json.dumps({
        'type': 'Success',
        'data':
            {
                'description': {
                    'profile': profile_object,
                    'coupons': coupons
                }
            }
    })


@high_api.route(f'{BASE_URI}/create_task', methods=['POST'])
def create_task() -> str:
    req = request.json
    try:
        token = request.headers['Authorization'].split(' ')[-1]
    except Exception as exp:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': str(exp)
            }
        })

    resp = check_profile_login(token)
    if type(resp) == str:
        return json.dumps(resp)
    else:
        profile, success = resp

    if type(profile) != AdminProfile:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'Only Admins can access these type of content!'
            }
        })

    resp, success = low_level_task_api.create_task(req)

    return json.dumps(resp)


@high_api.route(f'{BASE_URI}/get_task', methods=['GET'])
def get_task() -> str:
    req = request.json

    resp, success = low_level_task_api.get_task(req)

    return json.dumps(resp)


@high_api.route(f'{BASE_URI}/delete_task', methods=['POST'])
def delete_task() -> str:
    req = request.json
    try:
        token = request.headers['Authorization'].split(' ')[-1]
    except Exception as exp:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': str(exp)
            }
        })

    resp = check_profile_login(token)
    if type(resp) == str:
        return json.dumps(resp)
    else:
        profile, success = resp

    if type(profile) != AdminProfile:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'Only Admins can access these type of content!'
            }
        })

    resp, success = low_level_task_api.delete_task(req)

    return json.dumps(resp)


@high_api.route(f'{BASE_URI}/create_reward', methods=['POST'])
def create_reward():
    req = request.json
    try:
        token = request.headers['Authorization'].split(' ')[-1]
    except Exception as exp:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': str(exp)
            }
        })

    resp = check_profile_login(token)
    if type(resp) == str:
        return json.dumps(resp)
    else:
        profile, success = resp

    if type(profile) != AdminProfile:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'Only Admins can access these type of content!'
            }
        })

    resp, success = low_level_reward_api.create_reward(req)

    return json.dumps(resp)


@high_api.route(f'{BASE_URI}/get_reward', methods=['GET'])
def get_reward() -> str:
    """
    Payload kinézete:
    {
        'type': 'Reward',
        'data': {
            '_id': 'idvalue'
        }
    }

    :return:
    """
    req_data = request.json

    try:
        token = request.headers['Authorization'].split(' ')[-1]
    except Exception as exp:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': str(exp)
            }
        })

    if '_id' not in req_data['data']:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'ID should be provided!'
            }
        })

    resp = check_profile_login(token)

    if type(resp) == str:
        return json.dumps(resp)
    else:
        profile, success = resp

    reward_resp, reward_success = low_level_reward_api.get_reward(req_data)

    if not reward_success:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': reward_resp
            }
        })

    return json.dumps({
        'type': 'Success',
        'data': {
            'description': {
                '_id': str(reward_resp['data']['description'][0]['_id']),
                'title': reward_resp['data']['description'][0]['title'],
                'description': reward_resp['data']['description'][0]['description'],
                'company': reward_resp['data']['description'][0]['company'],
                'redeem_code': reward_resp['data']['description'][0]['redeem_code'],
                'expiration': reward_resp['data']['description'][0]['expiration']
            }
        }
    })


@high_api.route(f'{BASE_URI}/delete_reward', methods=['POST'])
def delete_reward():
    req = request.json
    try:
        token = request.headers['Authorization'].split(' ')[-1]
    except Exception as exp:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': str(exp)
            }
        })

    resp = check_profile_login(token)
    if type(resp) == str:
        return json.dumps(resp)
    else:
        profile, success = resp

    if type(profile) != AdminProfile:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'Only Admins can access these type of content!'
            }
        })

    resp, success = low_level_reward_api.delete_reward(req)

    return json.dumps(resp)


def get_mobile_task_screen():
    # ez csak 1 darab task teljes nézeete
    pass


def get_admin_main_screen():
    pass


@high_api.route(f'{BASE_URI}/admin_task_screen', methods=['GET'])
def get_admin_task_screen():
    # ha admin akkor az admin task screen
    # ha user akkor a user main screent
    pass


def get_mobile_rewards_screen():
    pass

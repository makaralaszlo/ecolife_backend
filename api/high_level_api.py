from flask import Blueprint, request
from bson.objectid import ObjectId
from config.api_config import BASE_URI
import api.low_level_api as low_level_api
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


def refresh_profile(profile_type: str, user_id: str):
    global users

    refreshed_user = low_level_profile_api.get_profile({
        'type': profile_type,
        'data': {
            '_id': ObjectId(user_id)
        }
    })

    for user in users:
        if user.get_id() == user_id:
            # TODO ez a hotflix nem biztos hogy jo amikor str kerul a user db-be
            if type(refreshed_user[0]) == UserProfile or type(refreshed_user[0]) == AdminProfile:
                user = refreshed_user[0]


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

    '''
    if type(profile) == UserProfile:
        refresh_profile('UserProfile', profile.get_id())
    elif type(profile) == AdminProfile:
        refresh_profile('AdminProfile', profile.get_id())
    '''
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

    old_task_list = profile.to_dict()['tasks']
    new_task_list = old_task_list.copy()
    # hozzá kell adni az elérhető vagy elfogadott vagy elutasitott taskokat a profilhoz

    all_task_list, all_task_success = low_level_task_api.get_all_task()
    if all_task_success:
        for task in all_task_list['data']['description']:
            if str(task['_id']) not in old_task_list:
                low_level_submit_api.create_submit({
                    'type': 'submit',
                    'data': {
                        'user_id': profile.get_id(),
                        'task_id': str(task['_id']),
                        'image': None,
                        'state': 'AVAILABLE'}
                })

                new_task_list.append(str(task['_id']))

        if new_task_list != old_task_list:
            low_level_profile_api.update_profile({
                'type': 'UserProfile',
                'data': {
                    'search': {
                        '_id': ObjectId(profile.get_id())
                    },
                    'update': {
                        'tasks': new_task_list
                    }
                }
            })

    task_list = new_task_list
    profile.set_tasks(task_list)

    # taskokat kell visszadni ami csak a rövid név, valami available, accepted, declined
    available_tasks = []
    accepted_tasks = []
    rejected_tasks = []
    pending_tasks = []

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
                task_resp['data']['description'][0]['_id'] = str(task_resp['data']['description'][0]['_id'])
                available_tasks.append(task_resp['data']['description'][0])
            elif str(submit_resp['data']['description'][0]['state']) == 'ACCEPTED':
                task_resp['data']['description'][0]['_id'] = str(task_resp['data']['description'][0]['_id'])
                accepted_tasks.append(task_resp['data']['description'][0])

                # TODO hozzá kell adni az id-t a rewadrdhoz

                profile_rewards = profile.to_dict()['rewards']
                if str(task_resp['data']['description'][0]['reward']) not in profile_rewards:
                    profile_rewards.append(str(task_resp['data']['description'][0]['reward']))

                    low_level_profile_api.update_profile({
                        'type': 'UserProfile',
                        'data': {
                            'search': {
                                '_id': ObjectId(profile.get_id())
                            },
                            'update': {
                                'rewards': profile_rewards
                            }
                        }
                    })

            elif str(submit_resp['data']['description'][0]['state']) == 'REJECTED':
                task_resp['data']['description'][0]['_id'] = str(task_resp['data']['description'][0]['_id'])
                rejected_tasks.append(task_resp['data']['description'][0])
            elif str(submit_resp['data']['description'][0]['state']) == 'PENDING':
                task_resp['data']['description'][0]['_id'] = str(task_resp['data']['description'][0]['_id'])
                pending_tasks.append(task_resp['data']['description'][0])

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

    profile_object = low_level_profile_api.get_profile({'type': 'UserProfile', 'data': {'_id': profile.get_id()}})
    coupons = []

    coupon_list = profile_object[0].to_dict()['rewards']
    for coupon in coupon_list:
        reward_resp, reward_success = low_level_reward_api.get_reward({
            'data': {
                '_id': coupon
            }
        })

        # TODO itt meg kell cisnálni hogy a reward_respből menejn közvetlen ki az adat ne igy!
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
                    'profile': profile_object[0].to_dict(),
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


@high_api.route(f'{BASE_URI}/user_task_details_screen', methods=['GET', 'POST'])
def user_get_task() -> str:
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

    if '_id' not in req_data['data']:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'ID should be provided!'
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

    task_resp, task_success = low_level_task_api.get_task(req_data)

    if not task_success:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': task_resp
            }
        })

    submit_resp, submit_success = low_level_submit_api.get_submit({
        'type': 'Submit',
        'data': {
            'user_id': profile.get_id(),
            'task_id': req_data['data']['_id']
        }
    })

    if not submit_success:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': submit_resp
            }
        })

    return json.dumps({
        'type': 'Success',
        'data': {
            'description': {
                'task': {
                    '_id': str(task_resp['data']['description'][0]['_id']),
                    'company': task_resp['data']['description'][0]['company'],
                    'reward': task_resp['data']['description'][0]['reward'],
                    'max_submission_number': task_resp['data']['description'][0]['max_submission_number'],
                    'immediately_evaluated': task_resp['data']['description'][0]['immediately_evaluated'],
                    'title': task_resp['data']['description'][0]['title'],
                    'description': task_resp['data']['description'][0]['description'],
                    'expiration': task_resp['data']['description'][0]['expiration']
                },
                'solution': {
                    'user_id': submit_resp['data']['description'][0]['user_id'],
                    'task_id': submit_resp['data']['description'][0]['task_id'],
                    'image': str(submit_resp['data']['description'][0]['image']),
                    'state': submit_resp['data']['description'][0]['state']
                }
            }
        }})


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


@high_api.route(f'{BASE_URI}/get_reward', methods=['GET', 'POST'])
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

    reward_list = low_level_profile_api.get_profile({
        'type': 'UserProfile',
        'data':{
            '_id': profile.get_id()
        }})[0].to_dict()['rewards']

    if str(req_data['data']['_id']) in reward_list:
        reward_list.remove(str(req_data['data']['_id']))

    low_level_profile_api.update_profile({
        'type': 'UserProfile',
        'data': {
            'search': {
                '_id': ObjectId(profile.get_id())
            },
            'update': {
                'rewards': reward_list
            }
        }
    })
    # reward_resp, reward_success = low_level_reward_api.delete_reward({'data': {'_id': req_data['data']['_id']}})

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


@high_api.route(f'{BASE_URI}/update_image', methods=['POST'])
def update_image() -> str:
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

    upload_res, upload_success = low_level_submit_api.update_submit(req, req['data']['state'])

    if not upload_success:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': upload_res
            }
        })

    # TODO nem nézzük hogy a max submission number 0 vagy alatta van -e
    if str(req['data']['state']) == 'ACCEPTED':
        task_data, task_success = low_level_task_api.get_task({
            'data': {
                '_id': req['data']['task_id']
            }
        })
        submission_counter = int(task_data['data']['description'][0]['max_submission_number']) - 1

        task_resp, task_success = low_level_task_api.decrease_counter(data={
            'data': {
                '_id': ObjectId(req['data']['task_id'])
            }
        }, max_submission_number=str(submission_counter))

    return json.dumps({
        'type': 'Success',
        'data': {
            'description': upload_res
        }
    })


@high_api.route(f'{BASE_URI}/admin_get_task', methods=['GET', 'POST'])
def get_admin_new_task_screen() -> str:
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

    task_data, task_success = low_level_task_api.get_task(data=req)

    if not task_success:
        return json.dumps(task_data)

    reward_data, reward_success = low_level_reward_api.get_reward(data={
        'data': {
            '_id': task_data['data']['description'][0]['reward']
        }
    })

    if not reward_success:
        return json.dumps(reward_data)

    submits_data, submits_success = low_level_submit_api.get_all_submit()

    if not submits_success:
        return json.dumps(submits_data)

    submits = []

    for submit in submits_data['data']['description']:
        if str(submit['task_id']) == req['data']['_id'] and submit['state'] == 'PENDING':
            submit['_id'] = str(submit['_id'])
            submits.append(submit)

    task_data['data']['description'][0]['_id'] = str(task_data['data']['description'][0]['_id'])
    reward_data['data']['description'][0]['_id'] = str(reward_data['data']['description'][0]['_id'])

    return json.dumps({
        'type': 'Success',
        'data': {
            'task': task_data['data']['description'][0],
            'reward': reward_data['data']['description'][0],
            'submit': submits
        }
    })


@high_api.route(f'{BASE_URI}/admin_create_new_task', methods=['POST'])
def admin_create_new_task():
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

    # TODO a reward expiration itt lehet állitani! never default most
    reward_resp, reward_success = low_level_reward_api.create_reward({
        'data': {
            'title': req['data']['reward_title'],
            'description': req['data']['reward_description'],
            'company': profile.to_dict()['company'],
            'redeem_code': '',
            'expiration': 'never'
        }
    })

    if not reward_success:
        return json.dumps(reward_resp)

    task_resp, task_success = low_level_task_api.create_task({
        'data': {
            'title': req['data']['task_title'],
            'company': profile.to_dict()['company'],
            'reward': reward_resp['data']['description'],
            'max_submission_number': req['data']['max_submission_number'],
            'immediately_evaluated': req['data']['immediately_evaluated'],
            'description': req['data']['task_description'],
            'expiration': 'never',
            'submits': []
        }
    })

    if not task_success:
        return json.dumps(task_resp)

    profile_tasks = profile.to_dict()['tasks']
    profile_rewards = profile.to_dict()['rewards']

    profile_tasks.append(task_resp['data']['description'])
    profile_rewards.append(reward_resp['data']['description'])

    profile_success = low_level_profile_api.update_profile(data={
        'type': 'AdminProfile',
        'data': {
            'search':
                {
                    '_id': ObjectId(profile.to_dict()['_id'])
                },
            'update':
                {
                    'rewards': profile_rewards,
                    'tasks': profile_tasks
                }
        }
    })

    return json.dumps({
        'type': 'Success',
        'data': {
            'task': task_resp,
            'reward': reward_resp,
        }
    })


@high_api.route(f'{BASE_URI}/admin_task_screen', methods=['GET', 'POST'])
def get_admin_task_screen() -> str:
    # TODO pending solutions is lehet le kellene legyen implementalva counter
    # ha admin akkor az admin task screen
    # ha user akkor a user main screent
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

    all_task_list, all_task_success = low_level_task_api.get_all_task()

    profiles = low_level_profile_api.get_profile({
        'type': 'AdminProfile',
        'data': {
            '_id': profile.get_id()
        }
    })

    # admin_own_tasks = profile.to_dict()['tasks']
    admin_own_tasks = profiles[0].to_dict()['tasks']

    if not all_task_success:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': all_task_list
            }
        })

    tasks = []
    # TODO ezt is a DB-ből kellene lekérni!
    task_list = profile.to_dict()['tasks']

    for task in all_task_list['data']['description']:
        if str(task['_id']) in admin_own_tasks:

            # TODO törölni kell azon task elemket aminek a max_submission_number <= 0
            if int(task['max_submission_number']) <= 0:
                task_list.remove(str(task['_id']))
                # task_data, task_success = low_level_task_api.delete_task({'data': {'_id': str(task['_id'])}})
            else:
                task['_id'] = str(task['_id'])
                tasks.append(task)

    # TODO ha 1 db task is 0-ára kerül a counterrel akkor az összessel együtt eltűnik
    low_level_profile_api.update_profile({
        'type': 'AdminProfile',
        'data': {
            'search': {
                '_id': ObjectId(profile.get_id())
            },
            'update': {
                'tasks': task_list
            }
        }
    })

    return json.dumps({
        'type': 'Success',
        'data': tasks
    })


@high_api.route(f'{BASE_URI}/upload_image', methods=['POST'])
def upload_image() -> str:
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

    if 'user_id' not in req_data['data'] or 'task_id' not in req_data['data']:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'The user_id and task_id should be provided!'
            }
        })

    if 'image' not in req_data['data']:
        return json.dumps({
            'type': 'Error',
            'data': {
                'description': 'Image is not attached to the request!'
            }
        })

    image = req_data['data']['image']

    task_data, task_success = low_level_task_api.get_task({'data': {'_id': req_data['data']['task_id']}})

    if not task_success:
        return json.dumps(task_data)

    # ha QR ez azt jelenti mert ha True akkor QR
    if task_data['data']['description'][0]['immediately_evaluated']:
        # a QR a task id-ből lett készitve, ha a TASK id és az image egyenlőre akkor automatikus accepted, egyébként rejected
        submit_data, submit_success = '', False
        if str(task_data['data']['description'][0]['_id']) == image:
            submit_data, submit_success = low_level_submit_api.update_submit(data={
                'data': {
                    'task_id': req_data['data']['task_id'],
                    'user_id': profile.get_id()
                }
            }, state='ACCEPTED')

            # TODO meg kellene nézni hogy nem e kisebb már mint 0 vagy 0 a max subbmission number igy!
            submission_counter = int(task_data['data']['description'][0]['max_submission_number']) - 1
            task_resp, task_success = low_level_task_api.decrease_counter(data={
                'data': {
                    '_id': ObjectId(req_data['data']['task_id'])
                }
            }, max_submission_number=str(submission_counter))
        else:
            submit_data, submit_success = low_level_submit_api.update_submit(data={
                'data': {
                    'task_id': req_data['data']['task_id'],
                    'user_id': profile.get_id()
                }
            }, state='REJECTED')
        return json.dumps(submit_data)

    else:
        upload_res, upload_success = low_level_api.upload_image_to_submit(req_data, image)

        if not upload_success:
            return json.dumps({
                'type': 'Error',
                'data': {
                    'description': upload_res
                }
            })

        return json.dumps({
            'type': 'Success',
            'data': {
                'description': upload_res
            }
        })

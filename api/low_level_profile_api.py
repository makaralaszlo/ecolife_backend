from flask import Blueprint, request
from config.api_config import BASE_URI
from database.database import DataBase
from objects.admin_profile import AdminProfile
from objects.user_profile import UserProfile
import json
import hashlib
import typing
from bson.objectid import ObjectId

low_api_profile = Blueprint(name='low_level_profile_api', import_name=__name__)
user_db = DataBase('EcoLife', 'user')
admin_db = DataBase('EcoLife', 'admin')


@low_api_profile.route(f'{BASE_URI}/create_profile', methods=['POST'])
def create_profile_endpoint() -> str:
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


@low_api_profile.route(f'{BASE_URI}/get_profile', methods=['GET'])
def get_profile_endpoint() -> str:
    """
    Payload kinézete AdminProfile esetén id-vel:
    {
        'type': 'AdminProfile',
        'data': {
                 '_id': str
                }
    }
    Payload kinézete UserProfile esetén id-vel:
    {
        'type': 'UserProfile',
        'data': {
                 '_id': str
                }
    }
    Payload kinézete AdminProfile esetén e-mail és jelszó alapján:
    {
        'type': 'AdminProfile',
        'data': {
                 'email_address': str,
                 'password': str,
                }
    }
    stb...

    Hiba visszatérés rossz type megadása esetén:
    {
        'type': 'Error',
        'data': {
                 'description': 'Incorrect type passed'
                }
    }

    :return:
    """
    req_data = request.json

    if '_id' in req_data['data']:
        req_data['data']['_id'] = ObjectId(req_data['data']['_id'])

    # ez csak akkor működik ha authentikációról van szó egyébként nem
    if 'password' in req_data['data'] and 'email_address' in req_data['data']:
        req_data['data']['password'] = hashlib.sha512((req_data['data']['password']).encode('utf-8')).hexdigest()

    if req_data['type'] == 'AdminProfile':
        db_resp, success = admin_db.get_element(req_data['data'])

        if not success:
            ret_data = {
                'type': 'Error',
                'data': {
                    'description': db_resp
                }
            }
        else:
            for element in db_resp:
                element['_id'] = str(element['_id'])
            ret_data = {
                'type': 'Success',
                'data': {
                    'description': db_resp
                }
            }

    elif req_data['type'] == 'UserProfile':
        db_resp, success = user_db.get_element(req_data['data'])

        if not success:
            ret_data = {
                'type': 'Error',
                'data': {
                    'description': db_resp
                }
            }
        else:
            for element in db_resp:
                element['_id'] = str(element['_id'])
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


@low_api_profile.route(f'{BASE_URI}/delete_profile', methods=['POST'])
def delete_profile_endpoint() -> str:
    """
    Payload kinézete AdminProfile esetén id-vel:
    {
        'type': 'AdminProfile',
        'data': {
                '_id': str
                }
    }
    Payload kinézete UserProfile esetén id-vel:
    {
        'type': 'UserProfile',
        'data': {
                '_id': str
                }
    }
    Payload kinézete AdminProfile esetén e-mail és jelszó alapján:
    {
        'type': 'AdminProfile',
        'data': {
                'email_address': str,
                'password': str,
                }
    }
    stb...

    Hiba visszatérés rossz type megadása esetén:
    {
        'type': 'Error',
        'data': {
                'description': 'Incorrect type passed'
                }
    }
    :return:
    """
    req_data = request.json

    if '_id' in req_data['data']:
        req_data['data']['_id'] = ObjectId(req_data['data']['_id'])

    if req_data['type'] == 'AdminProfile':
        db_resp, success = admin_db.delete_element(req_data['data'])

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
        db_resp, success = user_db.delete_element(req_data['data'])

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
                    'description': f'Successfully deleted {db_resp} element.'
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


def get_profile(data: dict) -> typing.Union[str, typing.List[AdminProfile], typing.List[UserProfile]]:
    """
    :return:
    """
    if '_id' in data['data']:
        data['data']['_id'] = ObjectId(data['data']['_id'])

    # ez csak akkor működik ha authentikációról van szó egyébként nem
    if 'password' in data['data'] and 'email_address' in data['data']:
        data['data']['password'] = hashlib.sha512((data['data']['password']).encode('utf-8')).hexdigest()

    if data['type'] == 'AdminProfile':
        db_resp, success = admin_db.get_element(data['data'])

        if not success:
            return 'Incorrect user data!'
        else:
            admin_profiles = []
            for element in db_resp:
                element['_id'] = str(element['_id'])
                admin_profiles.append(AdminProfile(_id=element['_id'],
                                                   email_address=element['email_address'],
                                                   first_name=element['first_name'],
                                                   last_name=element['last_name'],
                                                   date_of_birth=element['date_of_birth'],
                                                   password=element['password'],
                                                   company=element['company'],
                                                   tasks=element['tasks'],
                                                   rewards=element['rewards']))
            return admin_profiles

    elif data['type'] == 'UserProfile':
        db_resp, success = user_db.get_element(data['data'])

        if not success:
            return 'Incorrect user data!'
        else:
            user_profiles = []
            for element in db_resp:
                element['_id'] = str(element['_id'])
                user_profiles.append(UserProfile(_id=element['_id'],
                                                 email_address=element['email_address'],
                                                 first_name=element['first_name'],
                                                 last_name=element['last_name'],
                                                 date_of_birth=element['date_of_birth'],
                                                 password=element['password'],
                                                 rewards=element['rewards'],
                                                 tasks=element['tasks']
                                                 ))
            return user_profiles
    else:
        return 'Incorrect type passed'

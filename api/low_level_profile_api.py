from flask import Blueprint, request
from config.api_config import BASE_URI
from database.database import DataBase
from objects.admin_profile import AdminProfile
from objects.user_profile import UserProfile
import json


low_api_profile = Blueprint(name='low_level_profile_api', import_name=__name__)
user_db = DataBase('EcoLife', 'user')
admin_db = DataBase('EcoLife', 'admin')


@low_api_profile.route(f'{BASE_URI}/create_profile', methods=['POST'])
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


@low_api_profile.route(f'{BASE_URI}/get_profile', methods=['GET'])
def get_profile():
    pass


@low_api_profile.route(f'{BASE_URI}/delete_profile', methods=['POST'])
def delete_profile():
    pass

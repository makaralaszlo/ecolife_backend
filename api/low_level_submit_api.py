import typing
from flask import Blueprint
from objects.submit import Submit
from database.database import DataBase


low_api_submit = Blueprint(name='low_level_submit_api', import_name=__name__)
submit_db = DataBase('EcoLife', 'submit')


#@low_api_submit.route(f'{BASE_URI}/create_submit', methods=['POST'])
def create_submit(data: dict) -> typing.Tuple[dict, bool]:
    try:
        submit = Submit(user_id=data['data']['user_id'],
                        task_id=data['data']['task_id'],
                        image=data['data']['image'],
                        state=data['data']['state'])

        db_resp, success = submit_db.insert_element(
            search_data_dict={'user_id': data['data']['user_id'],
                              'task_id': data['data']['task_id']},
            insert_data_dict=submit.to_dict())

        if not success:
            return {
                       'type': 'Error',
                       'data': {
                           'description': db_resp
                       }
                   }, False
        else:
            return {
                       'type': 'Success',
                       'data': {
                           'description': db_resp
                       }
                   }, True

    except Exception as exp:
        return {
                   'type': 'Error',
                   'data': {
                       'description': str(exp)
                   }
               }, False


#@low_api_submit.route(f'{BASE_URI}/get_submit', methods=['GET'])
def get_submit(data: dict) -> typing.Tuple[dict, bool]:
    db_resp, success = submit_db.get_element({
        'user_id': data['data']['user_id'],
        'task_id': data['data']['task_id']
    })

    if not success:
        return {
                   'type': 'Error',
                   'data': {
                       'description': db_resp
                   }
               }, False
    else:
        return {
                   'type': 'Success',
                   'data': {
                       'description': db_resp
                   }
               }, True


#@low_api_submit.route(f'{BASE_URI}/delete_submit', methods=['POST'])
def delete_submit(data: dict) -> typing.Tuple[dict, bool]:
    db_resp, success = submit_db.delete_element({
        'user_id': data['data']['user_id'],
        'task_id': data['data']['task_id']
    })

    if not success:
        return {
                   'type': 'Error',
                   'data': {
                       'description': db_resp
                   }
               }, False
    else:
        return {
                   'type': 'Success',
                   'data': {
                       'description': db_resp
                   }
               }, True


def update_submit():
    # ezzel kell a módot változtatni egy submit esetében a state fieldet
    pass
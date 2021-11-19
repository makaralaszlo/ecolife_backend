import typing
from flask import Blueprint
from objects.task import Task
from database.database import DataBase
from bson.objectid import ObjectId

task_db = DataBase('EcoLife', 'tasks')

low_api_task = Blueprint(name='low_level_task_api', import_name=__name__)


def create_task(data: dict) -> typing.Tuple[dict, bool]:
    if '_id' in data['data']:
        return {
                   'type': 'Error',
                   'data': {
                       'description': 'ID should not be provided!'
                   }
               }, False

    try:
        task = Task(_id=data['data']['_id'] if '_id' in data['data'] else 'null',
                    company=data['data']['company'],
                    reward=data['data']['reward'],
                    max_submission_number=data['data']['max_submission_number'],
                    immediately_evaluated=data['data']['immediately_evaluated'],
                    title=data['data']['title'],
                    description=data['data']['description'],
                    expiration=data['data']['expiration'],
                    submits=data['data']['submits'])

        db_resp, success = task_db.insert_element(
            search_data_dict={'special_case': 'insert_anyway'},
            insert_data_dict=task.to_dict())

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


def get_task(data: dict) -> typing.Tuple[dict, bool]:
    if '_id' not in data['data']:
        return {
                   'type': 'Error',
                   'data': {
                       'description': 'ID should be provided!'
                   }
               }, False

    db_resp, success = task_db.get_element({'_id': ObjectId(data['data']['_id'])})

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


def delete_task(data: dict) -> typing.Tuple[dict, bool]:
    if '_id' not in data['data']:
        return {
                   'type': 'Error',
                   'data': {
                       'description': 'ID should be provided!'
                   }
               }, False

    db_resp, success = task_db.delete_element({'_id': ObjectId(data['data']['_id'])})

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


def get_all_task() -> typing.Tuple[dict, bool]:
    db_resp, success = task_db.get_element({})

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


if __name__ == '__main__':
    answ = create_task({
        'type': 'task',
        'data': {
            'title': 'teszt10',
            'description': 'ez egy test reward',
            'company': 'teszt.hu',
            'redeem_code': '12345678',
            'expiration': 'never',
            'reward': '618fabd6e8249d95d780e5c2',
            'immediately_evaluated': False,
            'max_submission_number': 2,
            'submits': []
        }
    })
    print(answ)
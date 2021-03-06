import typing
from flask import Blueprint
from objects.reward import Reward
from database.database import DataBase
from bson.objectid import ObjectId

low_api_reward = Blueprint(name='low_level_reward_api', import_name=__name__)
reward_db = DataBase('EcoLife', 'reward')


def create_reward(data: dict) -> typing.Tuple[dict, bool]:
    try:
        reward = Reward(_id=data['data']['_id'] if '_id' in data['data'] else 'null',
                        title=data['data']['title'],
                        description=data['data']['description'],
                        company=data['data']['company'],
                        redeem_code=data['data']['redeem_code'],
                        expiration=data['data']['expiration'])

        db_resp, success = reward_db.insert_element(
            search_data_dict={'special_case': 'insert_anyway'},
            insert_data_dict=reward.to_dict())

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


def get_reward(data: dict) -> typing.Tuple[dict, bool]:
    if '_id' not in data['data']:
        return {
                   'type': 'Error',
                   'data': {
                       'description': 'ID should be provided!'
                   }
               }, False

    db_resp, success = reward_db.get_element({'_id': ObjectId(data['data']['_id'])})

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


def delete_reward(data: dict) -> typing.Tuple[dict, bool]:
    if '_id' not in data['data']:
        return {
                   'type': 'Error',
                   'data': {
                       'description': 'ID should be provided!'
                   }
               }, False

    db_resp, success = reward_db.delete_element({'_id': ObjectId(data['data']['_id'])})

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



#if __name__ == '__main__':
#    answ = create_reward({
#        'type': 'reward',
#        'data': {
#            'title': 'teszt3',
#            'description': 'ez egy test reward',
#            'company': 'teszt.hu',
#            'redeem_code': '12345678',
#            'expiration': 'never'
#        }
#    })
#    print(answ)

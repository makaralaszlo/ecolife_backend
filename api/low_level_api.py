from flask import Blueprint
from database.database import DataBase
from config.api_config import BASE_URI
import typing
from PIL import Image
import io
import base64

low_api = Blueprint(name='low_level_api', import_name=__name__)
submit_db = DataBase('EcoLife', 'submit')


@low_api.route(f'{BASE_URI}/clear_database', methods=['POST'])
def clear_database():
    pass


def upload_image_to_submit(data: dict, image: typing.Any):
    submit_db.update_element(
        search_fields={
            'user_id': data['data']['user_id'],
            'task_id': data['data']['task_id']
        },
        update_data={
            'image': image,
            'state': 'PENDING'
        })

    return 'Image uploaded successfully!', True


from flask import Blueprint, request
from database.database import DataBase
from config.api_config import BASE_URI


low_api = Blueprint(name='low_level_api', import_name=__name__)


@low_api.route(f'{BASE_URI}/clear_database', methods=['POST'])
def clear_database():
    pass

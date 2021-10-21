from flask import Blueprint, request
from objects.submit import Submit
from database.database import DataBase
from config.api_config import BASE_URI


low_api_submit = Blueprint(name='low_level_submit_api', import_name=__name__)
submit_db = DataBase('EcoLife', 'submit')


@low_api_submit.route(f'{BASE_URI}/create_submit', methods=['POST'])
def create_submit():
    pass


@low_api_submit.route(f'{BASE_URI}/get_submit', methods=['GET'])
def get_submit():
    pass


@low_api_submit.route(f'{BASE_URI}/delete_submit', methods=['POST'])
def delete_submit():
    pass

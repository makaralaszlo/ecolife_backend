from flask import Blueprint, request
from objects.task import Task
from database.database import DataBase
from config.api_config import BASE_URI


low_api_task = Blueprint(name='low_level_task_api', import_name=__name__)
task_db = DataBase('EcoLife', 'task')


@low_api_task.route(f'{BASE_URI}/create_task', methods=['POST'])
def create_task():
    pass


@low_api_task.route(f'{BASE_URI}/get_task', methods=['GET'])
def get_task():
    pass


@low_api_task.route(f'{BASE_URI}/delete_task', methods=['POST'])
def delete_task():
    pass

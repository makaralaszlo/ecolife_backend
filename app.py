from flask import Flask, render_template
from api.low_level_api import low_api
from api.low_level_profile_api import low_api_profile
from api.low_level_reward_api import low_api_reward
from api.low_level_submit_api import low_api_submit
from api.low_level_task_api import low_api_task

from api.high_level_api import high_api


app = Flask(__name__)
app.register_blueprint(low_api)
app.register_blueprint(low_api_profile)
app.register_blueprint(low_api_reward)
app.register_blueprint(low_api_submit)
app.register_blueprint(low_api_task)

app.register_blueprint(high_api)


@app.route("/", methods=['GET'])
def hello():
    return render_template('swaggerui.html')


# TODO ezt törölni kell az Azure deployhoz
#if __name__ == '__main__':
#  app.run()

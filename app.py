from flask import Flask
from api.low_level_api import low_api


app = Flask(__name__)
app.register_blueprint(low_api)


@app.route("/")
def hello():
    return "Hello, World!"


# TODO ezt törölni kell az Azure deployhoz
if __name__ == '__main__':
    app.run()

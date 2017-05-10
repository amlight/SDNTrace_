from flask import Flask
from .home.controllers import home_blueprint
from .home.restful import restful_blueprint

# Register Flas blueprints
app = Flask(__name__,
            template_folder='templates')

app.register_blueprint(home_blueprint)
app.register_blueprint(restful_blueprint)

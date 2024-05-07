import datetime
import os

from .utils.Config import Config
from .utils.logger_models import *
import logging, pathlib, json, atexit
from logging.handlers import QueueListener, QueueHandler, RotatingFileHandler
from flask import Flask, render_template, g, request, redirect, url_for, current_app, session, abort, jsonify, flash, send_file
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from logging.config import dictConfig
from flask_mail import Mail, Message


def setup_logging():
    config_file = pathlib.Path("app/utils/logging_configdict.json")
    dict_config = None
    with open(config_file) as f_in:
        dict_config = json.load(f_in)

    log_queue = Queue()
    logging.config.dictConfig(dict_config)
    root_logger = logging.getLogger('root')
    queue_handler = QueueHandler(log_queue)
    root_logger.addHandler(queue_handler)
    queue_listener = QueueListener(log_queue, *logging.getLogger('notusable').handlers)
    # Iniciar el listener
    queue_listener.start()
    atexit.register(queue_listener.stop)


mail = Mail()
def create_app(logging_level='DEBUG',config_path:str='app/config.json',users_path:str='app/utils/users.json'):
    setup_logging()

    logger = logging.getLogger("init")

    config = Config(config_path)

    logging.basicConfig(level=config.LOG_LEVEL if config.LOG_LEVEL in ('DEBUG','INFO','WARNING','ERROR','CRITICAL') else 'DEBUG')

    users = Config(users_path)

    app = Flask(__name__)

    #Mail config
    app.config['MAIL_SERVER'] = config.MAIL_SERVER
    app.config['MAIL_PORT'] = config.MAIL_PORT
    app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
    app.config['MAIL_USE_SSL'] = config.MAIL_USE_SSL
    app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
    app.config['MAIL_DEFAULT_SENDER'] = config.MAIL_DEFAULT_SENDER

    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY

    os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY

    #Init mail
    appmail = mail.init_app(app)

    jwt = JWTManager(app)


    from .LangChainTopicSegment import LangChainTopicSegment_bp
    app.register_blueprint(LangChainTopicSegment_bp)

    @app.route("/register", methods=["POST"])
    def register():
        username = request.json.get("username")
        if username in users.attrs():
            return jsonify({"message": "User already exists"}), 400

        password = request.json.get("password")
        users[username] = password
        users.super_save("app/utils/users.json")

        return jsonify({"message": "User registered successfully"})

    @app.route("/login", methods=["POST"])
    def login():
        username = request.json.get("username")
        password = request.json.get("password")
        if username in users.attrs() and users[username] == password:
            expires = datetime.timedelta(hours=2)
            access_token = create_access_token(identity=username,expires_delta=expires)
            session['OPENAI_API_KEY'] = request.json.get('OPENAI_API_KEY','')
            return jsonify({"access_token": access_token})
        return jsonify({"message": "Invalid username or password"}), 401

    @app.route('/private')
    @jwt_required()
    def private():
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200

    return app
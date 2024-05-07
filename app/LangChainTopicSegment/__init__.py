from flask import Blueprint

LangChainTopicSegment_bp = Blueprint('LangChainTopicSegment',__name__,template_folder='templates')

from . import routes
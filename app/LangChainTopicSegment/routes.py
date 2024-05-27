import flask
from . import LangChainTopicSegment_bp
import requests, json
from flask import render_template, redirect, url_for, request, current_app, flash, abort, g, session, jsonify
from flask_mail import Message
from flask_jwt_extended import jwt_required
from .models import *
import logging

@LangChainTopicSegment_bp.route('/segmenttopics', methods=['POST'])
@jwt_required()
def SegmentTopics():
    logger = logging.getLogger(__name__)
    data = request.json
    if data is None or 'text' not in data:
        # Intentar como form-data si JSON falla o no contiene 'text'
        text = request.form.get('text')
        if not text:
            return jsonify({'error': 'No text provided'}), 400
    else:
        text = data['text']
    tipe = request.json.get('parse',None)
    if not tipe or not tipe in ['CATEGORY','TOPIC','SUBTOPIC']:
        return jsonify({'error': 'No parse type provided, select of: CATEGORY/TOPIC/SUBTOPIC'}), 400

    openai_api_key = session.get('openai_api_key',None) if session.get('openai_api_key',None) else request.json.get('OPENAI_API_KEY',None)
    if not openai_api_key:
        return jsonify({'error': 'No OpenAI API key provided nor on login'}), 400

    logger.info("All data received, starting process")
    try:
        docs,pr = Processer(text,openai_api_key=openai_api_key)
        logger.info(f"Docs obtained, {len(docs)}")
        unified = DocumentUnifier(docs,pr)
        logger.info(f"Docs unifying by {tipe}")
        if tipe == 'CATEGORY':
            docs = unified.unify_by_category()
        elif tipe == 'TOPIC':
            docs = unified.unify_by_topic()
        elif tipe == 'SUBTOPIC':
            docs = unified.unify_by_subtopic()
        logger.info(f"Docs unified by {tipe}, total: {len(docs)} topics")

    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        return jsonify({'error': f'Error processing text, error: {str(e)}'}), 500

    return json.dumps({'result': docs}), 200



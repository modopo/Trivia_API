import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def pagination(request, selection):
    page = request.args.get('page', 1, type=int)
    start = QUESTIONS_PER_PAGE * (page - 1)
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current = questions[start:end]

    return current


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resource={'/': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')

        return response

    @app.route('/categories')
    def get_all_categories():
        try:
            categories = Category.query.all()
            categories_dict = {}
            for category in categories:
                categories_dict[category.id] = category.type

            return jsonify({
                'success': True,
                'categories': categories_dict
            }), 200
        except Exception:
            abort(500)

    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        current_questions = pagination(request, questions)
        categories = Category.query.order_by(Category.id).all()

        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'sucess': True,
            'total_questions': len(questions),
            'categories': categories_dict,
            'questions': current_questions
        }), 200

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):

        try:
            question = Question.query.get(id)
            question.delete()

            return jsonify({
                'success': True,
                'message': "Question sccessfully deleted"
            }), 200
        except Exception:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        data = request.get_json()

        question = data.get('question', '')
        answer = data.get('answer', '')
        difficulty = data.get('difficulty', '')
        category = data.get('category', '')

        if question == '' or answer == '' or difficulty == '' or category == '':
            abort(422)

        try:
            question = Question(
                question=question,
                answer=answer,
                difficulty=difficulty,
                category=category
            )
            question.insert()

            return jsonify({
                'success': True,
                'message': 'Question successfully created.'
            }), 201
        except Exception:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        data = request.get_json()
        search_term = data.get('searchTerm', '')

        if search_term == '':
            abort(422)

        try:
            questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            if len(questions) == 0:
                abort(404)

            paginated_questions = pagination(request, questions)
            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(Question.query.all())
            }), 200
        except Exception:
            abort(404)

    @app.route('/categories/<int:id>/questions')
    def get_question_by_category(id):
        try:
            category = Category.query.filter_by(id=id).one_or_none()
            if category is None:
                abort(422)

            questions = Question.query.filter_by(category=id).all()
            paginated_questions = pagination(request, questions)

            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(questions),
                'current_category': category.type
            }), 200
        except Exception:
            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def play_question():

        data = request.get_json()
        prev_question = data.get('previous_questions')
        quiz_category = data.get('quiz_category')

        if quiz_category is None or prev_question is None:
            abort(400)

        if quiz_category['id'] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=quiz_category['id']).all()

        next_question = questions[random.randint(0, len(questions) - 1)]

        while next_question.id in prev_question:
            next_questions = questions[random.randint(0, len(questions) - 1)]

        return jsonify({
            'success': True,
            'question': next_question.format()
        }), 200

    # Error handler for bad request
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request error'
        }), 400

    # Error handler for resource not found
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    # Error handler for unprocessable entity (422)
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity'
        }), 422

    # Error handler for internal server error
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'An error has occured, please try again'
        }), 500

    return app

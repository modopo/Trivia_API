import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}@{}/{}".format('postgres:1234567890', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_all_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)

    def test_get_paginated(self):
        response = self.client().get('/questions?page=2')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)

    def test_out_of_bound(self):
        response = self.client().get('/questions?page=10000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_delete_question(self):
        new_question = Question(
            question='Test question to delete',
            answer='Answer to delete',
            difficulty=1,
            category=1
        )
        new_question.insert()
        new_id = new_question.id

        response = self.client().delete('/questions/{}'.format(new_id))
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully deleted')

    def test_delete_non_exist(self):
        response = self.client().delete('questions/129837')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_delete_invalid_id(self):
        response = self.client().delete('/questions/testingID')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_insert_question(self):
        new_question = {
            'question': 'Mock question',
            'answer': 'Mock answer',
            'difficulty': 1,
            'category': 1
        }

        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully created.')

    def test_insert_empty_field(self):
        new_question = {
            'question': 'Mock question',
            'answer': '',
            'difficulty': 1,
            'category': 1
        }

        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_search(self):
        search_term = {
            'searchTerm': 'peanut butter'
        }

        response = self.client().post('/questions/search', json=search_term)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

    def test_search_empty(self):
        search_term = {
            'searchTerm': ''
        }

        response = self.client().post('/questions/search', json=search_term)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_search_non_exist(self):
        search_term = {
            'searchTerm': 'asdf'
        }

        response = self.client().post('/questions/search', json=search_term)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_category_question(self):
        response = self.client().get('/categories/3/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Geography')

    def test_category_non_exist(self):
        response = self.client().get('/categories/5000/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_quiz(self):
        request_data = {
            'previous_questions': [2, 4],
            'quiz_category': {
                'type': 'Entertainment',
                'id': 5
            }
        }

        response = self.client().post('/quizzes', json=request_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        self.assertNotEqual(data['question']['id'], 2)
        self.assertNotEqual(data['question']['id'], 4)

        self.assertEqual(data['question']['category'], 5)


if __name__ == "__main__":
    unittest.main()
# Make the tests conveniently executable

from flask import Flask, request
from flask_restplus import Api, Resource, fields
from werkzeug.exceptions import BadRequest
import iso639

from engine.search_engine import SearchEngine, SearchCriteria
import logging

app = Flask(__name__)


# define which part of the engine json response to expose and how they will be rendered
def response_filter_render(base_response):
    response = dict()
    # book id
    response['id'] = base_response['_id']
    # title
    response['title'] = base_response['title']
    # authors
    authors = ''
    for author in base_response['authors']:
        name = author['name']
        if ',' in name:
            name = name.split(',')
            name = name[1].strip() + ' ' + name[0]
        authors += name + ', '
    response['authors'] = authors[:-2]
    # languages
    languages = ''
    for language in base_response['languages']:
        try:
         languages += iso639.to_name(language) + ', '
        except iso639.NonExistentLanguageError:
            languages += language + ', '
    response['languages'] = languages[:-2]
    # subjects
    subjects = ''
    for subject in base_response['subjects']:
        subjects += subject + ', '
    response['subjects'] = subjects[:-2]
    # cover link
    response['cover_link'] = base_response['cover_link']
    # link to read the book
    formats = base_response['formats']
    if 'text/html' in formats:
        response['link'] = formats['text/html']
    elif 'text/html; charset=utf-8' in formats:
        response['link'] = formats['text/html; charset=utf-8']
    elif 'text/html; charset=iso-8859-1' in formats:
        response['link'] = formats['text/html; charset=iso-8859-1']
    elif 'text/plain' in formats:
        response['link'] = formats['text/plain']
    else:
        response['link'] = formats['text/plain; charset=utf-8']

    return response


engine = SearchEngine(response_filter=response_filter_render)
logger = logging.getLogger(__name__)


# books api and api doc, use Swagger-ui
api = Api(app)

ns = api.namespace('books', description='Books Search API')

ss_model = ns.model('Simple Search Input', {
    'word': fields.String
})

as_model = ns.model('Advanced Search Input', {
    'pattern': fields.String,
    'title': fields.String,
    'language': fields.String,
    'subject': fields.String,
    'author': fields.String
})

sg_model = ns.model('Suggestions Input', {
    'book_id': fields.Integer
})

io_content_type = 'application/json'
io_content_type_error = 'request content-type must be json'
io_json_syntax_error = 'bad request, check your json syntax or content with the expected model'


@ns.route('/search')
@ns.expect(ss_model)
@ns.response(200, 'success')
@ns.response(400, 'bad request')
@ns.response(500, 'internal server error')
class SimpleSearchBooks(Resource):
    def post(self):
        try:
            # only json content-type requests are accepted
            if request.content_type != io_content_type:
                return {'error': io_content_type_error}, 400
            # in the case of a simple search, only the word to be searched for is required
            data = request.json
            if 'word' not in data:
                return {'error': 'missing parameter word'}, 400
            word = clean_arg(data['word'])
            # if the word size is less than 4, it is considered as a stop word
            if not word or len(word) < 3:
                return {'error': 'word value must be given with minimum length=4'}, 400

            return engine.simple_search(word), 200
        except BadRequest:
            return {'error': io_json_syntax_error}, 400
        # exception will be caught by the logger
        except Exception:
            logger.exception('exception occurred during simple search')
            return {'error': 'internal server error'}, 500


@ns.route('/suggestions')
@ns.expect(sg_model)
@ns.response(200, 'success')
@ns.response(400, 'bad request')
@ns.response(500, 'internal server error')
class Suggestions(Resource):
    def post(self):
        try:
            # input/output are json
            if request.content_type != io_content_type:
                return {'error': io_content_type_error}, 400
            data = request.json
            if 'book_id' not in data:
                return {'error': 'missing parameter book_id'}, 400
            book_id = data['book_id']

            return engine.similar_books(book_id), 200
        except BadRequest:
            return {'error': io_json_syntax_error}, 400
        except Exception:
            logger.exception('exception occurred during getting suggestions')


@ns.route('/advanced_search')
@ns.expect(as_model)
@ns.response(200, 'success')
@ns.response(400, 'bad request')
@ns.response(500, 'internal server error')
class AdvancedSearchBooks(Resource):
    def post(self):
        try:
            # only json content-type requests are accepted
            if request.content_type != io_content_type:
                return {'error': io_content_type_error}, 400
            # in advanced search: at least a pattern or search criteria must be given
            # pattern can be empty if at least one search criteria was given
            data = request.json
            author = subject = language = title = None
            pattern = ''
            # check if there is search criteria arguments and get values
            if 'author' in data:
                value = clean_arg(data['author'])
                if value:
                    author = value

            if 'subject' in data:
                value = clean_arg(data['subject'])
                if value:
                    subject = value

            if 'language' in data:
                value = clean_arg(data['language'])
                if value:
                    language = value

            if 'title' in data:
                value = clean_arg(data['title'])
                if value:
                    title = value

            if 'pattern' in data:
                value = clean_arg(data['pattern'])
                if value:
                    pattern = value

            if not(title or language or subject or author or pattern):
                return {'error': 'at least one criteria or pattern must be given'}, 400

            criteria = SearchCriteria(language=language, author=author, subject=subject, title=title)
            return engine.advanced_search(pattern, criteria)
        except BadRequest:
            return {'error': io_json_syntax_error}, 400
        except Exception:
            logger.exception('exception occurred during advanced search')
            return {'error': 'internal server error'}, 500


def clean_arg(arg: str) -> str:
    return arg.strip().lower()

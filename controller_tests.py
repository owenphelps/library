import nose
from nose.tools import raises, assert_equals, assert_in, assert_not_in
from nose.plugins.skip import SkipTest

from webtest import TestApp
from app import app

def setup():
    global app
    app = TestApp(app)

def test_main_entry_point_has_key_elements():
    res = app.get('/library/api')
    assert_in('services', res.json.keys())
    assert_in('documentation', res.json.keys())
    assert_in('books', res.json['services'].keys())
    assert_in('users', res.json['services'].keys())

    assert res.json['documentation'].endswith('/library/api/docs')

def test_no_book_found_throws_404():
    res = app.get('/library/api/books/NOTAREALISBN', status=404)

def test_new_book_works():
    res = app.put('/library/api/books/12345', '{"title":"TITLE", "description":"DESCRIPTION", "isbn":"ISBN"}', {'Content-Type': 'application/json; charset=utf-8'})
    assert_equals(res.status_code, 201)
    print res.json
    assert_equals(res.json['isbn'], 'ISBN')

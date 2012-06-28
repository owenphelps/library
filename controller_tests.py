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

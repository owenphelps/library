import nose
from nose.tools import raises, assert_equals, assert_in, assert_not_in
from nose.plugins.skip import SkipTest

from webtest import TestApp
from app import app

import json

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
    bk = dict(title="TITLE", description="DESCRIPTION", isbn="ISBN")
    res = app.put_json('/library/api/books/12345', bk, {'Content-Type': 'application/json; charset=utf-8'})
    assert_equals(res.status_code, 201)
    assert_equals(res.headers['Location'], 'http://localhost/library/api/books/ISBN')
    assert_equals(res.json['isbn'], 'ISBN')

def test_update_book_works():
    bk = dict(title="TITLE", description="DESCRIPTION", isbn="ISBN")
    res = app.put_json('/library/api/books/12345', bk, {'Content-Type': 'application/json; charset=utf-8'})
    bk['title'] = 'NEW TITLE'
    res = app.put_json('/library/api/books/12345', bk, {'Content-Type': 'application/json; charset=utf-8'})
    assert_equals(res.status_code, 200)
    assert_equals(res.headers['Location'], 'http://localhost/library/api/books/ISBN')
    assert_equals(res.json['title'], 'NEW TITLE')

def test_reserve_book_works():
    raise SkipTest()

def test_cancel_book_works():
    raise SkipTest()

def test_cancel_reserved_by_other_fails():
    raise SkipTest()

def test_borrow_book_works():
    raise SkipTest()

def test_return_book_works():
    raise SkipTest()

def test_return_borrowed_by_other_fails():
    raise SkipTest()

def test_return_not_borrowed_fails():
    raise SkipTest()

def test_borrow_borrowed_book_fails():
    raise SkipTest()

def test_list_many_books_uses_pagination():
    raise SkipTest()


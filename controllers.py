from bottle import route, request, response, get, post, put, abort
import json
from models import Book
from markdown import markdown

def get_prefix(request, path='/library/api'):
    urlparts = request.urlparts
    protocol = urlparts[0]
    domain = urlparts[1]
    if domain.endswith(':80'):
        domain = domain[:-3]

    return "%s://%s%s" % (protocol, domain, path)

@get('/library/api/')
@get('/library/api')
def library_api_root():
    prefix = get_prefix(request)
    return dict(
        documentation=prefix + "/docs",
        services=dict(
            books=prefix + "/books",
            users=prefix + "/users"
            )
        )

@get('/library/api/docs')
def docs():
    from os.path import split, join
    return markdown(open(join(split(__file__)[0], 'library_app.md'), 'r').read())

@get('/library/api/books/')
@get('/library/api/books')
def books():
    response.set_header('Content-Type', 'application/json')
    prefix = get_prefix(request)
    bks = [bk.to_json(prefix=prefix) for bk in Book.find()]
    return '[' + ',\n'.join(bks) + ']'

@get('/library/api/books/<book_id>')
def book_show(book_id):
    response.set_header('Content-Type', 'application/json')
    prefix = get_prefix(request)
    bk = Book.find_one(isbn=book_id)
    if bk:
        return bk.to_json(prefix=prefix)
    else:
        response.set_header('Content-Type', 'text/html')
        abort(404, "Can't find a book with that ISBN ('%s')." % book_id)

@put('/library/api/books/<book_id>')
def book_put(book_id):
    response.set_header('Content-Type', 'application/json')
    prefix = get_prefix(request)
    bk_input = request.json
    book = Book.find_one(isbn=bk_input['isbn'])
    if book:
        book.title = bk_input['title']
        book.description = bk_input['description']
    else:
        response.status = 201
        book = Book(bk_input['title'], bk_input['description'], bk_input['isbn'])
    Book.store(book)
    response.set_header('Location', prefix + '/books/' + book.isbn)
    return book.to_json(prefix)

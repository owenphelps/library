from bottle import route, request, response, get, post, abort
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
def library():
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
    return markdown(open('library_app.md', 'r').read())

@get('/library/api/books/<book_id>')
@get('/library/api/books/')
@get('/library/api/books')
def books(book_id=None):
    response.set_header('Content-Type', 'application/json')
    prefix = get_prefix(request)
    if book_id:
        the_book = Book.find_one(isbn=book_id)
        if the_book:
            return bk.to_json(prefix=prefix)
        else:
            response.set_header('Content-Type', 'text/html')
            abort(404, "Can't find a book with that ISBN ('%s')." % book_id)
    else:
        bks = [bk.to_json(prefix=prefix) for bk in Book.find()]

        return '[' + ',\n'.join(bks) + ']'

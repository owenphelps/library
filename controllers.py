import bottle
from bottle import route, run, debug, request, response, get, post, abort
import json
from models import Book
from markdown import markdown

def load_books():
    json_books = [json.loads(x) for x in open('library.json', 'r').read().splitlines()]
    books = [
        Book(j.get('title', ''), j.get('description', ''), j.get('ISBN', ''),
             author=j.get('author', ''),
             publisher=j.get('publisher', ''),
             small_thumbnail=j.get('small_thumbnail', ''),
             thumbnail=j.get('thumbnail', '')
             )
        for j in json_books
        ]
    return books

all_books = load_books()

@get('/test')
def test():
    print request.headers.keys()
    print request.query.keys()
    print request.forms.keys()
    print request.params.keys()
    print request.json
    print request.body.read()
    return "Hello again!"

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
        the_book = None
        for bk in all_books:
            if bk.isbn == book_id:
                the_book = bk
                break
        if the_book:
            return bk.to_json(prefix=prefix)
        else:
            response.set_header('Content-Type', 'text/html')
            abort(404, "Can't find a book with that ISBN ('%s')." % book_id)
    else:
        bks = [bk.to_json(prefix=prefix) for bk in all_books]

        return '[' + ',\n'.join(bks) + ']'

app = bottle.app()
if __name__=='__main__':
    debug(True)
    bottle.run(app=app, host='0.0.0.0', reloader=True)

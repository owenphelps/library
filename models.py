#!/usr/bin/env python
import json

# ----------------------------------------------------------------------

class AlreadyOnLoanError(Exception): pass
class BorrowingWhileReservedError(Exception): pass
class NotReservedError(Exception): pass
class NotCheckedOutError(Exception): pass
class NotTheBorrowerError(Exception): pass
class NoMatchingBookError(Exception): pass

# ----------------------------------------------------------------------

def equivalent_lists(first, second):
    assert_equals(sorted(first), sorted(second))

# ----------------------------------------------------------------------
class Repository(object):
    def __init__(self):
        self.books = []
    def find(self):
        return self.books[:]
#         if not cls._all_books:
#             json_books = [json.loads(x) for x in open('library.json', 'r').read().splitlines()]
#             books = [
#                 Book(j.get('title', ''), j.get('description', ''), j.get('ISBN', ''),
#                      author=j.get('author', ''),
#                      publisher=j.get('publisher', ''),
#                      small_thumbnail=j.get('small_thumbnail', ''),
#                      thumbnail=j.get('thumbnail', '')
#                      )
#                 for j in json_books
#                 ]
#             cls._all_books = books
#        return cls._all_books

    def find_one(self, isbn):
        ret = None
        for bk in self.find():
            if (not isbn) or (bk.isbn == isbn):
                ret = bk
                break
        return ret
    def store(self, book):
        self.books.append(book)

# ----------------------------------------------------------------------

class Book(object):
    BORROWED  = 'borrowed'
    AVAILABLE = 'available'

    CAN_RESERVE = 'can_reserve'
    CAN_BORROW  = 'can_borrow'
    CAN_RETURN  = 'can_return'
    CAN_CANCEL  = 'can_cancel'

    repository = None

    def __init__(self, title, description, isbn, borrower='', author='',
                 publisher='', small_thumbnail='', thumbnail='',
                 reservations=None):
        self.title = title
        self.description = description
        self.isbn = isbn
        self.borrower = borrower
        self.author = author
        self.publisher = publisher
        self.small_thumbnail = small_thumbnail
        self.thumbnail = thumbnail
        self.reservations = reservations or []
        
    def reserve(self, reserver):
        assert reserver and reserver.strip() != ''
        if not reserver in self.reservations:
            self.reservations.append(reserver)

    def un_reserve(self, reserver):
        assert reserver and reserver.strip() != ''
        if not reserver in self.reservations:
            raise NotReservedError('Not reserved by this user')
        self.reservations.remove(reserver)

    def check_out(self, borrower):
        assert borrower and borrower.strip() != ''

        if self.status() == Book.BORROWED:
            raise AlreadyOnLoanError('Already on loan')

        if self.reservations:
            if self.reservations[0] == borrower:
                self.reservations.pop(0)
            else:
                raise BorrowingWhileReservedError('Book is reserved')

        self.borrower = borrower

    def check_in(self, borrower):
        assert borrower and borrower.strip() != ''
        if self.status() != Book.BORROWED:
            raise NotCheckedOutError('Book is not checked out')
        if self.borrower != borrower:
            raise NotTheBorrowerError('User did not check out this book')

        self.borrower = ''

    def status(self):
        if self.borrower:
            return Book.BORROWED
        else:
            return Book.AVAILABLE

    def get_options(self, for_user):
        options = {}
        is_borrower       = self.borrower != '' and for_user == self.borrower
        is_reserver       = for_user in self.reservations
        is_first_reserver = is_reserver and self.reservations[0] == for_user

        options[Book.CAN_RESERVE] = not(is_borrower or is_reserver)
        options[Book.CAN_BORROW] = (is_first_reserver or not self.reservations) and not self.borrower
        options[Book.CAN_RETURN] = is_borrower
        options[Book.CAN_CANCEL] = is_reserver

        # Only return true values (makes using things easier).
        for key in options.keys():
            if not options[key]: options.pop(key) 
        return options

    def links(self, for_user='', prefix=''):
        ret = []
        options = self.get_options(for_user)

        ret.append(dict(rel='self', href=prefix + '/books/' + self.isbn))

        if options.get(Book.CAN_RESERVE, False):
            ret.append(dict(rel=prefix + '/docs#reserve', href=prefix + '/books/' + self.isbn + '/reservations'))

        if options.get(Book.CAN_BORROW, False):
            ret.append(dict(rel=prefix + '/docs#borrow', href=prefix + '/books/' + self.isbn + '/borrower'))

        if options.get(Book.CAN_RETURN, False):
            ret.append(dict(rel=prefix + '/docs#return', href=prefix + '/books/' + self.isbn + '/return'))

        if options.get(Book.CAN_CANCEL, False):
            ret.append(dict(rel=prefix + '/docs#cancel', href=prefix + '/books/' + self.isbn + '/reservations/' + for_user + '/cancel'))

        return ret

    def to_json(self, for_user='', prefix=''):
        js = dict(title=self.title,
                  description=self.description,
                  isbn=self.isbn,
                  borrower=self.borrower,
                  reservations=self.reservations,
                  author=self.author,
                  publisher=self.publisher,
                  small_thumbnail=self.small_thumbnail,
                  thumbnail=self.thumbnail,
                  _links=self.links(for_user, prefix))
        return json.dumps(js, indent=2)

    @classmethod
    def find(cls):
        if not cls.repository:
            cls.repository = Repository()
        return cls.repository.find()

    @classmethod
    def find_one(cls, isbn=None):
        if not cls.repository:
            cls.repository = Repository()
        return cls.repository.find_one(isbn)

    @classmethod
    def store(cls, book):
        if not cls.repository:
            cls.repository = Repository()
        cls.repository.store(book)

# ----------------------------------------------------------------------

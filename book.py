#!/usr/bin/env python
import nose
from nose.tools import raises, assert_equals, assert_in, assert_not_in
from nose.plugins.skip import SkipTest
import json

# ----------------------------------------------------------------------

class AlreadyOnLoanError(Exception): pass
class BorrowingWhileReservedError(Exception): pass
class NotReservedError(Exception): pass
class NotCheckedOutError(Exception): pass
class NotTheBorrowerError(Exception): pass

# ----------------------------------------------------------------------

def equivalent_lists(first, second):
    assert_equals(sorted(first), sorted(second))

# ----------------------------------------------------------------------

class Book(object):
    BORROWED  = 'borrowed'
    AVAILABLE = 'available'

    CAN_RESERVE = 'can_reserve'
    CAN_BORROW  = 'can_borrow'
    CAN_RETURN  = 'can_return'
    CAN_CANCEL  = 'can_cancel'

    def __init__(self, title, description, isbn, borrower='', reservers=None):
        self.title = title
        self.description = description
        self.isbn = isbn
        self.borrower = borrower
        self.reservers = reservers or []
        
    def reserve(self, reserver):
        assert reserver and reserver.strip() != ''
        if not reserver in self.reservers:
            self.reservers.append(reserver)

    def un_reserve(self, reserver):
        assert reserver and reserver.strip() != ''
        if not reserver in self.reservers:
            raise NotReservedError('Not reserved by this user')
        self.reservers.remove(reserver)

    def check_out(self, borrower):
        assert borrower and borrower.strip() != ''

        if self.status() == Book.BORROWED:
            raise AlreadyOnLoanError('Already on loan')

        if self.reservers:
            if self.reservers[0] == borrower:
                self.reservers.pop(0)
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
        is_reserver       = for_user in self.reservers
        is_first_reserver = is_reserver and self.reservers[0] == for_user

        options[Book.CAN_RESERVE] = not(is_borrower or is_reserver)
        options[Book.CAN_BORROW] = (is_first_reserver or not self.reservers) and not self.borrower
        options[Book.CAN_RETURN] = is_borrower
        options[Book.CAN_CANCEL] = is_reserver

        # Only return true values.
        for key in options.keys():
            if not options[key]: options.pop(key) 
        return options

    def links(self, for_user='', options=None):
        ret = []
        options = options or self.get_options(for_user)

        if options.get(Book.CAN_RESERVE, False):
            ret.append(dict(rel='reserve', href='/book/' + self.isbn + '/reservations'))

        if options.get(Book.CAN_BORROW, False):
            ret.append(dict(rel='borrow', href='/book/' + self.isbn + '/borrower'))

        if options.get(Book.CAN_RETURN, False):
            ret.append(dict(rel='return', href='/book/' + self.isbn + '/return'))

        if options.get(Book.CAN_CANCEL, False):
            ret.append(dict(rel='cancel', href='/book/' + self.isbn + '/reservations/' + for_user + '/cancel'))

        return ret

    def to_json(self, for_user=''):
        js = dict(title=self.title,
                  description=self.description,
                  isbn=self.isbn,
                  borrower=self.borrower,
                  reservers=self.reservers,
                  _links=self.links(for_user))
        return json.dumps(js)

# ----------------------------------------------------------------------

def test_book_class_empty():
    book = Book('', '', '')
    assert_equals(book.title, '')
    assert_equals(book.description, '')
    assert_equals(book.isbn, '')
    assert_equals(book.status(), Book.AVAILABLE)

def test_book_class_populated_with_no_borrower():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    assert_equals(book.title, 'TITLE')
    assert_equals(book.description, 'DESCRIPTION')
    assert_equals(book.isbn, 'ISBN')
    assert_equals(book.status(), Book.AVAILABLE)

def test_book_class_populated_with_borrower_is_borrowed():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN', 'BORROWER')
    assert_equals(book.borrower, 'BORROWER')
    assert_equals(book.status(), Book.BORROWED)

def test_book_class_with_reservers():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN', 'BORROWER', ['RESERVER1', 'RESERVER2'])
    assert_equals(len(book.reservers), 2)

# ----------------------------------------------------------------------

def test_book_can_reserve_new_book():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')

    assert_equals(len(book.reservers), 1)
    assert_in('RESERVER', book.reservers)

def test_book_can_reserve_new_book_once():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')

    book.reserve('RESERVER')
    assert_equals(len(book.reservers), 1)
    assert_in('RESERVER', book.reservers)

def test_book_can_reserve_new_book_with_more_than_one_user():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')
    book.reserve('ANOTHER RESERVER')

    assert_equals(len(book.reservers), 2)
    assert_equals('RESERVER', book.reservers[0])
    assert_equals('ANOTHER RESERVER', book.reservers[1])

def test_book_can_un_reserve_book():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')
    book.reserve('ANOTHER RESERVER')
    book.reserve('YET ANOTHER RESERVER')

    book.un_reserve('ANOTHER RESERVER')
    book.un_reserve('RESERVER')
    book.un_reserve('YET ANOTHER RESERVER')
    assert_equals(0, len(book.reservers))

@raises(NotReservedError)
def test_book_cannot_un_reserve_book_when_not_reserved_by_you():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')

    book.un_reserve('ANOTHER RESERVER')

def test_book_borrow_new_book():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.check_out('BORROWER')
    assert_equals(book.status(), Book.BORROWED)
    assert_equals(book.borrower, 'BORROWER')

# ----------------------------------------------------------------------

@raises(AlreadyOnLoanError)
def test_book_can_only_be_borrowed_once():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.check_out('BORROWER')

    book.check_out('ANOTHER BORROWER')

@raises(BorrowingWhileReservedError)
def test_book_cannot_be_borrowed_when_reserved():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')

    book.check_out('BORROWER')

def test_book_can_borrow_reserved_book_if_only_reserver():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')

    book.check_out('RESERVER')

    assert_equals(len(book.reservers), 0)

def test_book_can_borrow_reserved_book_if_first_reserver():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')
    book.reserve('ANOTHER RESERVER')

    book.check_out('RESERVER')

    assert_equals(len(book.reservers), 1)
    assert_equals('ANOTHER RESERVER', book.reservers[0])

@raises(BorrowingWhileReservedError)
def test_book_cannot_borrow_reserved_book_if_later_reserver():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')
    book.reserve('ANOTHER RESERVER')

    book.check_out('ANOTHER RESERVER')

# ----------------------------------------------------------------------

def test_book_can_return_book_if_borrower():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.check_out('BORROWER')

    book.check_in('BORROWER')

@raises(NotTheBorrowerError)
def test_book_cannot_return_book_if_not_borrower():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.check_out('BORROWER')

    book.check_in('ANOTHER BORROWER')

@raises(NotCheckedOutError)
def test_book_cannot_return_book_if_not_checked_out():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')

    book.check_in('BORROWER')

# ----------------------------------------------------------------------

def test_options_no_borrower():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')

    expected = { Book.CAN_RESERVE: True, Book.CAN_BORROW: True }
    assert_equals(expected, book.get_options('SOMEONE'))

def test_options_no_borrower_with_one_reserver_by_reserver():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')

    expected = { Book.CAN_BORROW: True, Book.CAN_CANCEL: True }
    assert_equals(expected, book.get_options('RESERVER'))

def test_options_no_borrower_with_one_reserver_by_other():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')

    expected = { Book.CAN_RESERVE: True }
    assert_equals(expected, book.get_options('OTHER'))

def test_options_no_borrower_with_many_reservers_by_reserver():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')
    book.reserve('RESERVER 2')
    book.reserve('RESERVER 3')

    expected = { Book.CAN_BORROW: True, Book.CAN_CANCEL: True }
    assert_equals(expected, book.get_options('RESERVER'))

def test_options_no_borrower_with_many_reservers_by_other():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')
    book.reserve('RESERVER 2')
    book.reserve('RESERVER 3')

    expected = { Book.CAN_RESERVE: True }
    assert_equals(expected, book.get_options('OTHER'))

def test_options_with_borrower():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.check_out('BORROWER')

    expected = { Book.CAN_RESERVE: True }
    assert_equals(expected, book.get_options('OTHER'))

def test_options_for_borrower():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.check_out('BORROWER')

    expected = { Book.CAN_RETURN: True }
    assert_equals(expected, book.get_options('BORROWER'))

def test_options_with_borrower_with_many_reservers_by_reserver():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.check_out('BORROWER')
    book.reserve('RESERVER')
    book.reserve('RESERVER 2')
    book.reserve('RESERVER 3')

    expected = {}
    expected[Book.CAN_CANCEL]  = True
    assert_equals(expected, book.get_options('RESERVER'))

# ----------------------------------------------------------------------

def test_links_reserve():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')

    options = { Book.CAN_RESERVE: True }
    assert_equals(dict(rel='reserve', href='/book/ISBN/reservations'), book.links('RESERVER', options)[0])

def test_links_borrow():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')

    options = { Book.CAN_BORROW: True }
    assert_equals(dict(rel='borrow', href='/book/ISBN/borrower'), book.links('SOMEONE', options)[0])

def test_links_return():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')

    options = { Book.CAN_RETURN: True }
    assert_equals(dict(rel='return', href='/book/ISBN/return'), book.links('BORROWER', options)[0])

def test_links_cancel():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')

    options = { Book.CAN_CANCEL: True }
    assert_equals(dict(rel='cancel', href='/book/ISBN/reservations/RESERVER/cancel'), book.links('RESERVER', options)[0])


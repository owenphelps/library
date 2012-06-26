#!/usr/bin/env python
import nose
from nose.tools import raises, assert_equals, assert_in, assert_not_in
from nose.plugins.skip import SkipTest
import pyDoubles.framework as mock
import json

from library_model import (Book, AlreadyOnLoanError, BorrowingWhileReservedError,
                  NotReservedError, NotCheckedOutError, NotTheBorrowerError)

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
    assert_equals(len(book.reservations), 2)

# ----------------------------------------------------------------------

def test_book_can_reserve_new_book():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')

    assert_equals(len(book.reservations), 1)
    assert_in('RESERVER', book.reservations)

def test_book_can_reserve_new_book_once():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')

    book.reserve('RESERVER')
    assert_equals(len(book.reservations), 1)
    assert_in('RESERVER', book.reservations)

def test_book_can_reserve_new_book_with_more_than_one_user():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')
    book.reserve('ANOTHER RESERVER')

    assert_equals(len(book.reservations), 2)
    assert_equals('RESERVER', book.reservations[0])
    assert_equals('ANOTHER RESERVER', book.reservations[1])

def test_book_can_un_reserve_book():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')
    book.reserve('ANOTHER RESERVER')
    book.reserve('YET ANOTHER RESERVER')

    book.un_reserve('ANOTHER RESERVER')
    book.un_reserve('RESERVER')
    book.un_reserve('YET ANOTHER RESERVER')
    assert_equals(0, len(book.reservations))

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

    assert_equals(len(book.reservations), 0)

def test_book_can_borrow_reserved_book_if_first_reserver():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.reserve('RESERVER')
    book.reserve('ANOTHER RESERVER')

    book.check_out('RESERVER')

    assert_equals(len(book.reservations), 1)
    assert_equals('ANOTHER RESERVER', book.reservations[0])

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
    expected[Book.CAN_CANCEL] = True
    assert_equals(expected, book.get_options('RESERVER'))

# ----------------------------------------------------------------------

def test_links_reserve():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.get_options = mock.method_returning({ Book.CAN_RESERVE: True })

    assert_equals(dict(rel='self', href='/books/ISBN'), book.links('RESERVER')[0])
    assert_equals(dict(rel='reserve', href='/books/ISBN/reservations'), book.links('RESERVER')[1])

def test_links_borrow():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.get_options = mock.method_returning({ Book.CAN_BORROW: True })

    assert_equals(dict(rel='self', href='/books/ISBN'), book.links('SOMEONE')[0])
    assert_equals(dict(rel='borrow', href='/books/ISBN/borrower'), book.links('SOMEONE')[1])

def test_links_return():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.get_options = mock.method_returning({ Book.CAN_RETURN: True })

    assert_equals(dict(rel='self', href='/books/ISBN'), book.links('BORROWER')[0])
    assert_equals(dict(rel='return', href='/books/ISBN/return'), book.links('BORROWER')[1])

def test_links_cancel():
    book = Book('TITLE', 'DESCRIPTION', 'ISBN')
    book.get_options = mock.method_returning({ Book.CAN_CANCEL: True })

    assert_equals(dict(rel='self', href='/books/ISBN'), book.links('RESERVER')[0])
    assert_equals(dict(rel='cancel', href='/books/ISBN/reservations/RESERVER/cancel'), book.links('RESERVER')[1])

# ----------------------------------------------------------------------

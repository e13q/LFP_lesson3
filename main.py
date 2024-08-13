import urllib3
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

import os


SUB_DIR_NAME = 'Books'


def check_for_redirect(response):
    if len(response.history) > 0:
        raise requests.exceptions.TooManyRedirects


def save_book(book, book_name):
    if not os.path.exists(SUB_DIR_NAME):
        os.makedirs(SUB_DIR_NAME)
    with open(f"./{SUB_DIR_NAME}/{book_name}.txt", "wb") as f:
        f.write(book)
        f.close()


def get_title_and_author(response):
    soup = BeautifulSoup(response.text, 'lxml')
    title_and_author = soup.find(id='content').find('h1').text
    title, author = tuple(title_and_author.split(' \xa0 :: \xa0 '))
    return sanitize_filename(title), author


def fetch_book_info(book_id):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(
        url
    )
    response.raise_for_status()
    check_for_redirect(response)
    return response


def get_book(book_id):
    url = 'https://tululu.org/txt.php'
    response = requests.get(
        url,
        params={
            'id': book_id
        }
    )
    response.raise_for_status()
    check_for_redirect(response)
    return response.content


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    for book_id in range(1, 11):
        try:
            book = get_book(book_id)
            response_book_info = fetch_book_info(book_id)
            title, author = get_title_and_author(response_book_info)
            save_book(book, title)
        except (requests.exceptions.HTTPError):
            print(f'HTTPerror {requests.exceptions.HTTPError.response.text}')
        except (requests.exceptions.TooManyRedirects):
            print(f'Website page for book id {book_id} has been moved')

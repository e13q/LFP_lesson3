import urllib3
import urllib.parse
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

import os


SUB_DIR_NAME_BOOKS = 'Books'
SUB_DIR_NAME_COVERS = 'Images'


def check_for_redirect(response):
    if len(response.history) > 0:
        raise requests.exceptions.TooManyRedirects


def save_book_txt(book, book_name):
    if not os.path.exists(SUB_DIR_NAME_BOOKS):
        os.makedirs(SUB_DIR_NAME_BOOKS)
    with open(f"./{SUB_DIR_NAME_BOOKS}/{book_name}.txt", "wb") as f:
        f.write(book)
        f.close()


def fetch_book_cover(cover_path):
    cover_url = f'https://tululu.org{cover_path}'
    response = requests.get(
        url=cover_url
    )
    response.raise_for_status()
    check_for_redirect(response)
    return response.content    


def save_book_cover(cover, img_ext,book_name):
    if not os.path.exists(SUB_DIR_NAME_COVERS):
        os.makedirs(SUB_DIR_NAME_COVERS)
    with open(f"./{SUB_DIR_NAME_COVERS}/{book_name}.{img_ext}", "wb") as f:
        f.write(cover)
        f.close()


def parse_book_page(book_page):
    soup = BeautifulSoup(book_page, 'lxml')
    title_and_author = soup.find(id='content').find('h1').text
    title, author = tuple(title_and_author.split(' \xa0 :: \xa0 '))
    title_safe = sanitize_filename(title)
    cover_path = soup.find(class_='bookimage').find('img')['src']
    return title_safe, author, cover_path


def fetch_book_page(book_id):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(
        url
    )
    response.raise_for_status()
    check_for_redirect(response)
    return response.text


def fetch_book(book_id):
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
            book = fetch_book(book_id)
            book_page = fetch_book_page(book_id)
            title, author, cover_path = parse_book_page(book_page)
            save_book_txt(book, title)
            cover = fetch_book_cover(cover_path)
            _, img_ext = tuple(cover_path.split('.'))
            save_book_cover(cover, img_ext, title)
        except (requests.exceptions.HTTPError):
            print(f'HTTPerror {requests.exceptions.HTTPError.response.text}')
        except (requests.exceptions.TooManyRedirects):
            print(f'Website page for book id {book_id} has been moved')

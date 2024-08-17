import urllib3
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin

import os
import argparse
import time

BASE_URL = 'https://tululu.org'


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.TooManyRedirects


def save_object(object, directory, title, type):
    os.makedirs(directory, exist_ok=True)
    if type == 'txt':
        write_type = 'w'
    else:
        write_type = 'wb'
    with open(f"./{directory}/{title}.{type}", write_type) as file:
        if object.__class__ == list:
            for sub_object in object:
                if write_type == 'w' and sub_object.__class__ == bytes:
                    sub_object = sub_object.decode()
                file.write(f'{sub_object}\n\n')
        else:
            if write_type == 'w' and object.__class__ == bytes:
                object = object.decode()
            file.write(object)


def parse_book_page(book_page):
    soup = BeautifulSoup(book_page, 'lxml')
    title_and_author = soup.find(id='content').find('h1').text
    title, author = tuple(title_and_author.split(' \xa0 :: \xa0 '))
    title_safe = sanitize_filename(title)
    cover_path = soup.find(class_='bookimage').find('img')['src']
    comments_raw = soup.find_all(class_='texts')
    comments = [comment_raw.find('span').text for comment_raw in comments_raw]
    genres_raw = soup.find('span', class_='d_book').find_all('a')
    genres = [genre_raw.text for genre_raw in genres_raw]
    return title_safe, author, cover_path, comments, genres


def save_book(id):
    book = fetch_data(urljoin(BASE_URL, '/txt.php'), {'id': book_id})
    if not book:
        return
    book_page = fetch_data(urljoin(BASE_URL, f'/b{book_id}/'), is_text=True)
    if not book_page:
        return
    (
        title, author, cover_path, comments, genres
    ) = parse_book_page(book_page)
    cover = fetch_data(urljoin(BASE_URL, cover_path))
    _, img_ext = tuple(cover_path.split('.'))
    save_object(book, 'Books', title, 'txt')
    save_object(cover, 'Covers', title, img_ext)
    save_object(comments, 'Comments', title, 'txt')
    save_object(genres, 'Genres', title, 'txt')


def fetch_data(url, params=None, is_text=False, retries=3, delay=4):
    for attempt in range(retries):
        try:
            response = requests.get(url, params, timeout=10)
            response.raise_for_status()
            check_for_redirect(response)
            if is_text:
                return response.text
            return response.content
        except (requests.ConnectionError, requests.Timeout):
            print(
                f'An attempt to connect {attempt + 1} of {retries} failed'
            )
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                print('All attempts have been exhausted.')
                return None
        except requests.exceptions.HTTPError as e:
            print(f'HTTPerror {e}')
            return None
        except requests.exceptions.TooManyRedirects:
            print(f'Website page for book id {book_id} has been moved')
            return None
        except requests.RequestException as e:
            print(f'Request exception: {e}')
            return None


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    parser = argparse.ArgumentParser(
        description='Download books from https://tululu.org')
    parser.add_argument(
        'id_from',
        help='Book id from',
        nargs='?',
        type=int,
        default=1
    )
    parser.add_argument(
        'id_to',
        help='Book id to',
        nargs='?',
        type=int,
        default=10
    )
    parser = parser.parse_args()
    id_from = parser.id_from
    id_to = parser.id_to
    for book_id in range(id_from, id_to+1):
        save_book(book_id)

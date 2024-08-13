import urllib3
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

import os
import argparse


SUB_DIR_NAME_BOOKS = 'Books'
SUB_DIR_NAME_COVERS = 'Covers'
SUB_DIR_NAME_COMMENTS = 'Comments'
SUB_DIR_NAME_GENRES = 'Genres'


def check_for_redirect(response):
    if len(response.history) > 0:
        raise requests.exceptions.TooManyRedirects


def fetch_book_cover(cover_path):
    cover_url = f'https://tululu.org{cover_path}'
    response = requests.get(
        url=cover_url
    )
    response.raise_for_status()
    check_for_redirect(response)
    return response.content


def save_book_genres(genres, book_name):
    if not os.path.exists(SUB_DIR_NAME_GENRES):
        os.makedirs(SUB_DIR_NAME_GENRES)
    with open(f"./{SUB_DIR_NAME_GENRES}/{book_name}.txt", "w") as file:
        for genre in genres:
            file.write(f'{genre}\n')
        file.close()


def save_book_comments(comments, book_name):
    if not os.path.exists(SUB_DIR_NAME_COMMENTS):
        os.makedirs(SUB_DIR_NAME_COMMENTS)
    with open(f"./{SUB_DIR_NAME_COMMENTS}/{book_name}.txt", "w") as file:
        for comment in comments:
            file.write(f'{comment}\n\n')
        file.close()


def save_book_cover(cover, img_ext, book_name):
    if not os.path.exists(SUB_DIR_NAME_COVERS):
        os.makedirs(SUB_DIR_NAME_COVERS)
    with open(f"./{SUB_DIR_NAME_COVERS}/{book_name}.{img_ext}", "wb") as file:
        file.write(cover)
        file.close()


def save_book_txt(book, book_name):
    if not os.path.exists(SUB_DIR_NAME_BOOKS):
        os.makedirs(SUB_DIR_NAME_BOOKS)
    with open(f"./{SUB_DIR_NAME_BOOKS}/{book_name}.txt", "wb") as file:
        file.write(book)
        file.close()


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


def save_book(id):
    book = fetch_book(book_id)
    book_page = fetch_book_page(book_id)
    (
        title, author, cover_path, comments, genres
    ) = parse_book_page(book_page)
    save_book_txt(book, title)
    cover = fetch_book_cover(cover_path)
    _, img_ext = tuple(cover_path.split('.'))
    save_book_cover(cover, img_ext, title)
    save_book_comments(comments, title)
    save_book_genres(genres, title)


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
        default=11
    )
    parser = parser.parse_args()
    id_from = parser.id_from
    id_to = parser.id_to
    for book_id in range(id_from, id_to):
        try:
            save_book(book_id)
        except (requests.exceptions.HTTPError):
            print(f'HTTPerror {requests.exceptions.HTTPError.response.text}')
        except (requests.exceptions.TooManyRedirects):
            print(f'Website page for book id {book_id} has been moved')

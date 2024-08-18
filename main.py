import urllib3
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin

import os
import argparse
import time
from tqdm.auto import tqdm

BASE_URL = 'https://tululu.org'


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.TooManyRedirects


def save_object(object, directory, title, file_type='txt'):
    if not object:
        return
    os.makedirs(directory, exist_ok=True)
    write_type = 'w'
    if file_type != 'txt':
        write_type = 'wb'
    with open(f"./{directory}/{title}.{file_type}", write_type) as file:
        if object.__class__ == list:
            for sub_object in object:
                file.write(f'{sub_object}\n\n')
        else:
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


def save_book(book_id):
    book = fetch_data(
        urljoin(BASE_URL, '/txt.php'), {'id': book_id}
    )
    if not book:
        return
    else:
        book = book.text
    book_page_url = urljoin(BASE_URL, f'/b{book_id}/')
    book_page = fetch_data(book_page_url)
    if not book_page:
        return
    else:
        book_page = book_page.text
    (
        title, author, cover_path, comments, genres
    ) = parse_book_page(book_page)
    cover = fetch_data(urljoin(book_page_url, cover_path)).content
    _, img_ext = tuple(cover_path.split('.'))
    save_object(book, 'Books', title)
    save_object(cover, 'Covers', title, img_ext)
    save_object(comments, 'Comments', title)
    save_object(genres, 'Genres', title)


def fetch_data(url, params=None, retries=3, delay=4):
    for attempt in range(retries):
        try:
            response = requests.get(url, params, timeout=10)
            response.raise_for_status()
            check_for_redirect(response)
            return response
        except (requests.ConnectionError, requests.Timeout):
            tqdm.write(
                f'An attempt to connect {attempt + 1} of {retries} failed'
            )
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                tqdm.write('All attempts have been exhausted.')
                return None
        except requests.exceptions.HTTPError as e:
            tqdm.write(f'HTTPerror {e}')
            return None
        except requests.exceptions.TooManyRedirects:
            tqdm.write(f'Webpage for id {params.get('id')} has been moved')
            return None
        except requests.RequestException as e:
            tqdm.write(f'Request exception: {e}')
            return None


def main():
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
    for book_id in tqdm(
        range(id_from, id_to+1), ascii=True, desc='Download books'
    ):
        save_book(book_id)


if __name__ == '__main__':
    main()

import urllib3
import requests
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
            save_book(book, book_id)
        except (requests.exceptions.HTTPError):
            print(f'HTTPerror {requests.exceptions.HTTPError.response.text}')
        except (requests.exceptions.TooManyRedirects):
            print(f'Website page for book id {book_id} has been moved')

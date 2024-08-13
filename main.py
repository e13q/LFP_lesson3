import urllib3
import requests
import os


SUB_DIR_NAME = 'Books'


def save_book(book):
    with open(f"./{SUB_DIR_NAME}/{id}.txt", "wb") as f:
        f.write(book)


def get_book(book_id):
    url = 'https://tululu.org/txt.php'
    response = requests.get(
        url,
        params={
            'id': book_id
        },
        allow_redirects=False
    )
    response.raise_for_status()
    if response.status_code == 302:
        raise requests.exceptions.TooManyRedirects
    return response.content


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    if not os.path.exists(SUB_DIR_NAME):
        os.makedirs(SUB_DIR_NAME)
    try:
        for book_id in range(1, 11):
            get_book(book_id)
    except (requests.exceptions.HTTPError):
        print(f'HTTPerror {requests.exceptions.HTTPError.response.text}')
    except (requests.exceptions.TooManyRedirects):
        print('Website page has been moved')

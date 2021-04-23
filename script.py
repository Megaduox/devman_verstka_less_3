import requests
import os

from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def check_for_redirect(response_check):
    if response_check.history:
        raise requests.HTTPError
    else:
        pass


def download_txt(path='books', counter=1, root_url='https://tululu.org/txt.php', all_pages=11):
    if not os.path.exists(path):
        os.makedirs(path)
    while counter < all_pages:
        payload = {'id': counter}
        response = requests.get(root_url, verify=False, params=payload)
        html_page = f'https://tululu.org/b{counter}/'
        response_html_page = requests.get(html_page, verify=False)
        try:
            check_for_redirect(response)
            response.raise_for_status()
            check_for_redirect(response_html_page)
            response_html_page.raise_for_status()
            soup = BeautifulSoup(response_html_page.text, 'lxml')
            book_name_author_all_text_from_h1 = soup.find('h1').text.split('::')
            book_name = book_name_author_all_text_from_h1[0].strip()
            filename = sanitize_filename(f'{book_name}.txt')
            with open(os.path.join(path, filename), 'wb') as file:
                file.write(response.content)
            counter += 1
        except requests.HTTPError:
            counter += 1


download_txt()

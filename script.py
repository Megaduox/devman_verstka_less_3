import requests
import os

from urllib.parse import urljoin
from urllib.parse import unquote

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
            book_image_short_url = soup.find('div', class_='bookimage').find('img')['src']
            book_image_full_url = urljoin('https://tululu.org/', book_image_short_url)
            with open(os.path.join(path, filename), 'wb') as file:
                file.write(response.content)
            counter += 1
        except requests.HTTPError:
            counter += 1


def download_image(path='images', all_pages=10, counter=5):
    if not os.path.exists(path):
        os.makedirs(path)
    while counter < all_pages:
        html_page = f'https://tululu.org/b{counter}/'
        response_html_page = requests.get(html_page, verify=False)
        try:
            check_for_redirect(response_html_page)
            response_html_page.raise_for_status()
            soup = BeautifulSoup(response_html_page.text, 'lxml')
            book_image_short_url = soup.find('div', class_='bookimage').find('img')['src']
            book_image_full_url = urljoin('https://tululu.org/', book_image_short_url)
            filename = unquote(book_image_full_url.split('/')[-1])
            response_image = requests.get(book_image_full_url, verify=False)
            check_for_redirect(response_image)
            response_image.raise_for_status()
            with open(os.path.join(path, filename), 'wb') as file:
                file.write(response_image.content)
            counter += 1
        except requests.HTTPError:
            counter += 1


def parse_book_comments(soup):
    comments_text = soup.find_all('div', class_='texts')
    for comment in comments_text:
        comment_text = comment.find('span', class_='black').text
        print(comment_text)


def get_comments_and_genres(all_pages=11, counter=1):
    while counter < all_pages:
        html_page = f'https://tululu.org/b{counter}/'
        response_html_page = requests.get(html_page, verify=False)
        try:
            check_for_redirect(response_html_page)
            response_html_page.raise_for_status()
            soup = BeautifulSoup(response_html_page.text, 'lxml')
            book_name_author_all_text_from_h1 = soup.find('h1').text.split('::')
            book_name = book_name_author_all_text_from_h1[0].strip()
            all_book_genres = soup.find('span', class_='d_book')
            book_genres = all_book_genres.find_all('a')
            for genr in book_genres:
                print('Жанр(ы) книги:', genr.text)
            print('Название книги:', book_name)
            parse_book_comments(soup)
            counter += 1
        except requests.HTTPError:
            counter += 1


def parse_book_page(soup):
    book_information = {}
    all_comments = []
    all_genres = []

    book_name_author_all_text_from_h1 = soup.find('h1').text.split('::')
    book_information['Название книги'] = book_name_author_all_text_from_h1[0].strip()
    book_information['Автор книги'] = book_name_author_all_text_from_h1[-1].strip()
    book_image_short_url = soup.find('div', class_='bookimage').find('img')['src']
    book_information['Ссылка на обложку'] = urljoin('https://tululu.org/', book_image_short_url)
    all_book_genres = soup.find('span', class_='d_book')
    book_genres = all_book_genres.find_all('a')
    for genr in book_genres:
        all_genres.append(genr.text)
    book_information['Жанр(-ы) книги'] = all_genres
    comments_text = soup.find_all('div', class_='texts')
    for comment in comments_text:
        comment_text = comment.find('span', class_='black').text
        all_comments.append(comment_text)
    book_information['Комментарии'] = all_comments

    return book_information


html_page = 'https://tululu.org/b9/'
response_html_page = requests.get(html_page, verify=False)
try:
    check_for_redirect(response_html_page)
    response_html_page.raise_for_status()
    soup = BeautifulSoup(response_html_page.text, 'lxml')
    print(parse_book_page(soup))
except requests.HTTPError:
    print('Ошибка запроса к странице')
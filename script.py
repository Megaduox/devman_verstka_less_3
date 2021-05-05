import requests
import os
import argparse

from urllib.parse import urljoin
from urllib.parse import unquote

from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def check_for_redirect(response_check):
    if response_check.history:
        raise requests.HTTPError
    else:
        pass


def download_txt(response, response_html_page, path='books'):
    os.makedirs(path, exist_ok=True)
    check_for_redirect(response)
    response.raise_for_status()
    check_for_redirect(response_html_page)
    response_html_page.raise_for_status()
    soup = BeautifulSoup(response_html_page.text, 'lxml')
    book_name_and_author = soup.find('h1').text.split('::')
    book_name = book_name_and_author[0].strip()
    filename = sanitize_filename(f'{book_name}.txt')
    with open(os.path.join(path, filename), 'wb') as file:
        file.write(response.content)


def download_image(response_html_page, path='images'):
    os.makedirs(path, exist_ok=True)
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


def parse_book_comments(soup):
    comments_text = soup.find_all('div', class_='texts')
    for comment in comments_text:
        comment_text = comment.find('span', class_='black').text
    return comment_text


def get_comments_and_genres(start_page, end_page):
    for page in range(start_page, end_page):
        html_page = f'https://tululu.org/b{page}/'
        response_html_page = requests.get(html_page, verify=False)
        check_for_redirect(response_html_page)
        response_html_page.raise_for_status()
        soup = BeautifulSoup(response_html_page.text, 'lxml')
        book_name_and_author = soup.find('h1').text.split('::')
        book_name, book_author = book_name_and_author
        all_book_genres = soup.find('span', class_='d_book')
        book_genres = all_book_genres.find_all('a')
        print('Название книги:', book_name)
        print('Автор книги:', book_author)
        for genr in book_genres:
            print('Жанр(ы) книги:', genr.text)
        print('Комментарии:', parse_book_comments(soup), sep='\n')


def parse_book_page(soup):
    book_information = {}
    book_name_and_author = soup.find('h1').text.split('::')
    book_information['Название книги'], book_information['Автор книги'] = book_name_and_author
    book_image_short_url = soup.find('div', class_='bookimage').find('img')['src']
    book_information['Ссылка на обложку'] = urljoin('https://tululu.org/', book_image_short_url)
    all_book_genres = soup.find('span', class_='d_book')
    book_genres = all_book_genres.find_all('a')
    all_genres = [genr.text for genr in book_genres]
    book_information['Жанр(-ы) книги'] = all_genres
    comments_text = soup.find_all('div', class_='texts')
    book_information['Комментарии'] = [comment.find('span', class_='black').text for comment in comments_text]
    return book_information


def main(start_book_id, end_book_id, root_url='https://tululu.org/txt.php'):
    for book_id in range(start_book_id, end_book_id+1):
        payload = {'id': book_id}
        response = requests.get(root_url, verify=False, params=payload)
        html_page = f'https://tululu.org/b{book_id}/'
        response_html_page = requests.get(html_page, verify=False)
        download_txt(response, response_html_page)
        download_image(response_html_page)
        get_comments_and_genres(start_book_id, end_book_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''
    Скрипт парсинга книг из онлайн-библиотеки tululu.org.
    Для работы скрипта задайте два аргумента - с какой по какую
    страницу парсить. Если ничего не задать - скрипт
    по умолчанию скачает первые 10 страниц библиотеки.
    Первый аргумент - начальная страница, второй - конечная страница.
    ''')
    parser.add_argument('start_id', help='Начальная страница', type=int, default=1, nargs='?')
    parser.add_argument('end_id', help='Конечная страница', type=int, default=10, nargs='?')
    args = parser.parse_args()
    try:
        main(args.start_id, args.end_id)
    except requests.HTTPError:
        print('Ошибка при запросе')
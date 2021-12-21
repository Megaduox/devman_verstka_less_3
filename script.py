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


def download_txt(book_id, book_name, path='books'):
    root_url = 'https://tululu.org/txt.php'
    payload = {'id': book_id}
    response = requests.get(root_url, verify=False, params=payload)
    response.raise_for_status()

    os.makedirs(path, exist_ok=True)

    filename = sanitize_filename(f'{book_name}.txt')
    with open(os.path.join(path, filename), 'wb') as file:
        file.write(response.content)


def download_image(book_url):
    path = 'images'
    os.makedirs(path, exist_ok=True)
    filename = unquote(book_url.split('/')[-1])
    response_image = requests.get(book_url, verify=False)
    with open(os.path.join(path, filename), 'wb') as file:
        file.write(response_image.content)


def get_comments_and_genres(soup):
    book_name_and_author = soup.find('h1').text.split('::')
    book_name = book_name_and_author[0].strip()
    book_author = book_name_and_author[-1].strip()
    all_book_genres = soup.find('span', class_='d_book')
    book_genres = all_book_genres.find_all('a')
    print('Название книги:', book_name)
    print('Автор книги:', book_author)
    for genr in book_genres:
        print('Жанр(ы) книги:', genr.text)
    all_comments = [comment.find('span', class_='black').text for comment in soup.find_all('div', class_='texts')]
    print(all_comments)


def parse_book_page(soup):

    book_name_and_author = soup.find('h1').text.split('::')
    book_image_short_url = soup.find('div', class_='bookimage').find('img')['src']
    book_name, book_author = book_name_and_author

    all_book_genres = soup.find('span', class_='d_book')
    book_genres = all_book_genres.find_all('a')
    all_genres = [genr.text for genr in book_genres]

    book_information = {
        'Название книги': book_name.strip(),
        'Автор книги': book_author.strip(),
        'Ссылка на обложку': urljoin('https://tululu.org/', book_image_short_url),
        'Жанр(-ы) книги': all_genres,
    }

    comments_text = soup.find_all('div', class_='texts')
    all_comments = [comment.find('span', class_='black').text for comment in comments_text]

    return book_information


def main():
    parser = argparse.ArgumentParser(description='Скрипт парсинга книг из онлайн-библиотеки tululu.org.'
                                                 'Для работы скрипта задайте два аргумента - с какой по какую'
                                                 'страницу парсить. Если ничего не задать - скрипт'
                                                 'по умолчанию скачает первые 10 страниц библиотеки.'
                                                 'Первый аргумент - начальная страница, второй - конечная страница.')
    parser.add_argument('start_id', help='Начальная страница', type=int, default=1, nargs='?')
    parser.add_argument('end_id', help='Конечная страница', type=int, default=10, nargs='?')
    args = parser.parse_args()

    for book_id in range(args.start_id, args.end_id+1):

        book_url = f'https://tululu.org/b{book_id}/'
        try:
            response_html_page = requests.get(book_url, verify=False)
            response_html_page.raise_for_status()
            check_for_redirect(response_html_page)
            soup = BeautifulSoup(response_html_page.text, 'lxml')
            book_info = parse_book_page(soup)
            download_txt(book_id, book_info['Название книги'])
            download_image(book_info['Ссылка на обложку'])
            get_comments_and_genres(soup)
        except requests.HTTPError as e:
            print(f'Ошибка HTTP: {e}')


if __name__ == '__main__':
    main()

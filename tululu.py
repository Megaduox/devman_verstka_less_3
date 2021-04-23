import requests

from bs4 import BeautifulSoup

url = 'https://tululu.org/b1/'
response = requests.get(url, verify=False)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')
book_name_author_all_text_from_h1 = soup.find('h1').text.split('::')
book_name = book_name_author_all_text_from_h1[0].strip()
book_author = book_name_author_all_text_from_h1[1].strip()

print('Автор: ', book_author)
print('Название книги: ', book_name)
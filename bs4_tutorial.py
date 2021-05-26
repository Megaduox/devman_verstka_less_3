import requests

from bs4 import BeautifulSoup

url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')
post_name = soup.find('h1', class_='entry-title').text
post_image = soup.find('img', class_='attachment-post-image')['src']
post_text = soup.find('div', class_='entry-content').text

print('post_name: ', post_name)
print('post_image: ', post_image)
print('post_text: ', post_text)

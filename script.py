import requests
import os


counter = 1
all_pages = 11
path = 'books'

if not os.path.exists(path):
    os.makedirs(path)

while counter < all_pages:
    url = f'https://tululu.org/txt.php?id={counter}'
    response = requests.get(url, verify=False)
    response.raise_for_status()
    filename = f'id={counter}.txt'
    with open(os.path.join(path, filename), 'wb') as file:
        file.write(response.content)
    print(response.status_code)
    counter += 1

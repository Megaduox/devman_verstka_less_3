import requests
import os


counter = 1
all_pages = 11
path = 'books'

if not os.path.exists(path):
    os.makedirs(path)


def check_for_redirect(response_check):
    if response_check.history:
        raise requests.HTTPError
    else:
        pass


while counter < all_pages:
    payload = {'id': counter}
    url = f'https://tululu.org/txt.php'
    response = requests.get(url, verify=False, params=payload)
    try:
        check_for_redirect(response)
        response.raise_for_status()
        filename = f'id={counter}.txt'
        with open(os.path.join(path, filename), 'wb') as file:
            file.write(response.content)
        counter += 1
    except requests.HTTPError:
        counter += 1






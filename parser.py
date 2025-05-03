import requests
from bs4 import BeautifulSoup


def get_flowers():
    session = requests.session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) '
                      'Gecko/20100101 Firefox/128.0'
    }
    session.headers.update(headers)
    response = session.get(url='https://ru.freepik.com/photos/flower')
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    figure = soup.find_all('figure')
    flowers = []
    for i in figure:
        img = i.find('img')
        flowers.append(img.get('data-src'))
    return flowers


def cats_url():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) '
                      'Gecko/20100101 Firefox/128.0'
    }
    status_code = requests.get(
        'https://api.thecatapi.com/v1/images/search').status_code
    if status_code == 200:
        return (requests.get('https://api.thecatapi.com/v1/images/search',
                             headers=headers)
                .json()[0].get('url'))
    return f'Сервер вернул {status_code}'

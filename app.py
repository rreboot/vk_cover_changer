from jinja2 import Template
import requests
import imgkit
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ERROR_CODES = {
    1: 'UNKNOWN ERROR',
    2: 'APPLICATION NOT STARTED',
    3: 'UNKNOWN METHOD',
    4: 'BAD SIGN',
    5: 'INVALID TOKEN',
    6: 'TOO MANY REQUESTS PER SECOND',
    7: 'PERMISSION DENIED',
    8: 'INVALID REQUEST',
    9: 'FLOOD CONTROL',
    10: 'INTERNAL SERVER ERROR',
    14: 'CAPTCHA NEEDED',
}


with open('token') as f:
    ACCESS_TOKEN = f.read().strip()

API_VERSION = '5.92'
GROUP_ID = '164254021'


def request_to_api(method, pars):
    return requests.post('https://api.vk.com/method/{}'.format(method), params=pars).json()


def main_loop():
    parameters = {'group_id': GROUP_ID,
                  'sort': 'time_desc',
                  'count': 1,
                  'fields': 'photo_200',
                  'v': API_VERSION,
                  'access_token': ACCESS_TOKEN,
                  }
    response = request_to_api('groups.getMembers', parameters)

    first_name = response['response']['items'][0]['first_name']
    last_name = response['response']['items'][0]['last_name']
    photo = response['response']['items'][0]['photo_200']

    # converter

    with open('templates/index.html', 'r') as f:
        template = Template(f.read())

    tmp = template.render(first_name=first_name,
                          last_name=last_name,
                          avatar=photo)

    with open('templates/index_tmp.html', 'w') as f:
        f.write(tmp)

    imgkit.from_file('templates/index_tmp.html', 'out.png')

    # загрузка обложки

    parameters = {'group_id': GROUP_ID,
                  'v': API_VERSION,
                  'access_token': ACCESS_TOKEN,
                  'crop_x': 0,
                  'crop_y': 0,
                  'crop_x2': 1590,
                  'crop_y2': 400
                  }
    response = request_to_api('photos.getOwnerCoverPhotoUploadServer', parameters)

    upload_url = response['response']['upload_url']
    image_file = {'file': open('out.png', 'rb')}

    response = requests.post(upload_url, files=image_file).json()

    upload_hash = response['hash']
    photo = response['photo']

    parameters = {
        'hash': upload_hash,
        'photo': photo,
        'access_token': ACCESS_TOKEN,
        'v': API_VERSION}
    response = request_to_api('photos.saveOwnerCoverPhoto', parameters)
    print(response)


if __name__ == '__main__':
    while True:
        main_loop()
        time.sleep(60)


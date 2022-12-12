import requests
import os
import datetime
import json


class VK2YaDiskBackup:
    base_url = 'https://cloud-api.yandex.net/v1/disk'
    log = []

    def __init__(self, vk_owner_id, vk_token, yadisk_token):
        self.owner = vk_owner_id
        self.vk_token = vk_token
        self.session = requests.session()
        self.session.headers = {'Accept': 'application/json',
                                'Authorization': 'OAuth ' + yadisk_token}

        pass

    def get_vk_profile_photos_list(self, album_id='profile'):
        url = f"https://api.vk.com/method/photos.get?owner_id={self.owner}" \
              f"&album_id={album_id}&extended=1&access_token={self.vk_token}&v=5.131"
        resp = requests.get(url)
        if resp.status_code == 200:
            out = {}
            for image in resp.json()['response']['items']:
                out[image['id']] = {'comments': image['comments']['count'],
                                    'likes': image['likes']['count'],
                                    'size': image['sizes'][-1]['type'],
                                    'url': image['sizes'][-1]['url'],
                                    'date': image['date']}
            return out
        else:
            return None

    def download_files_from_vk(self, url, to_folder='img'):
        file_name = str(url).split('?size')[0].split('/')[-1]
        if not os.path.isdir(os.path.join(os.getcwd(), to_folder)):
            os.mkdir(os.path.join(os.getcwd(), to_folder))
        file_name = os.path.join(os.getcwd(), to_folder, file_name)
        print(file_name)
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(file_name, 'wb') as file:
                for chunk in r.iter_content(1024):
                    file.write(chunk)

    def yadisk_upload_file(self, image: dict, base_dir='img'):
        folder_resp = self.session.put(f'{self.base_url}/resources?path={base_dir}')
        if folder_resp.status_code == 409 or folder_resp.status_code == 201:
            file_url = self.session.get(f'{self.base_url}/resources/upload?path={base_dir}/' \
                                        f'{str(image["likes"])}.jpg&overwrite=false')
            yadisk_file_name = f'{str(image["likes"])}.jpg'
            if file_url.status_code == 409:
                file_url = self.session.get(
                    f'{self.base_url}/resources/upload?path={base_dir}/{str(image["likes"])}_' \
                    f'{datetime.datetime.fromtimestamp(image["date"]).strftime("%Y%m%d")}.jpg&overwrite=false')
                yadisk_file_name = f'{str(image["likes"])}_' \
                                   f'{datetime.datetime.fromtimestamp(image["date"]).strftime("%Y%m%d")}.jpg'
            file_name = str(image['url']).split('?size')[0].split('/')[-1]
            file_name = os.path.join(os.getcwd(), 'img', file_name)
            print(image['url'])
            with open(file_name, 'rb') as file:
                restp = self.session.post(file_url.json()['href'], files={'file': file})
                if restp.status_code == 201:
                    self.log.append({"file_name": yadisk_file_name,
                                     "size": image['size']})


if __name__ == "__main__":
    if os.getenv('token', default=None) is not None and os.getenv('owner_id', default=None) is not None \
            and os.getenv('YaDisk_token', default=None) is not None:
        app = VK2YaDiskBackup(vk_token=os.getenv('token', default=None),
                              vk_owner_id=os.getenv('owner_id', default=None),
                              yadisk_token=os.getenv('YaDisk_token', default=None))
        #Базовая работа
        vk_photo_list = app.get_vk_profile_photos_list()
        if vk_photo_list != None:
            for image in vk_photo_list:
                app.download_files_from_vk(url=vk_photo_list[image]['url'])
                app.yadisk_upload_file(vk_photo_list[image])
                with open('logs.json', 'w') as outfile:
                    json.dump(app.log, outfile)
        # Загрузка из Альбома
        vk_photo_list = app.get_vk_profile_photos_list(album_id='276363897')
        if vk_photo_list != None:
            for image in vk_photo_list:
                app.download_files_from_vk(url=vk_photo_list[image]['url'])
                app.yadisk_upload_file(vk_photo_list[image], base_dir='vk_albom')
                with open('logs2.json', 'w') as outfile:
                    json.dump(app.log, outfile)


import requests
import json
from project import cache

pullzone_url = "http://91b52230aa5a5ff.b-cdn.net"

#   Получение каталогов в пути CDN и вывод их в виде словаря
@cache.cached(timeout=600)
def opendir(path="/ap4uklor/"):
    url = r"https://storage.bunnycdn.com" + path
    AccessKey = "46aefc84-581b-4624-8bdd3e0cbb15-cc91-47f6"
    headers = {
        "Accept": "application/json",
        "AccessKey": AccessKey
    }
    response = requests.get(url, headers=headers)
    data = json.loads(response.content)

    dirs = {}
    for c in data:
        if c['IsDirectory']:
            dirs[c['ObjectName']] = {"path": c['Path']}

    return dirs


#   Получение списка файлов в пути CDN и вывод их в виде словаря
@cache.cached(timeout=600)
def showfiles(path):
    url = r"https://storage.bunnycdn.com" + path
    AccessKey = "46aefc84-581b-4624-8bdd3e0cbb15-cc91-47f6"
    headers = {
        "Accept": "application/json",
        "AccessKey": AccessKey
    }

    response = requests.get(url, headers=headers)
    data = json.loads(response.content)

    files = {}
    for c in data:
        if c['IsDirectory'] is False:
            files[c['ObjectName']] = {"path": c['Path']}

    return files

@cache.cached(timeout=600)
def filesfromfolder(path="/ap4uklor/"):
    #print("Path в bunnycdn" + path)
    dirfiles = showfiles(path)
    imgs, videos = [], []
    for f in dirfiles:
        # Вывод изображений
        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
            imgs.append(f)
        # Вывод видеофайлов
        elif f.lower().endswith('.mp4'):
            videos.append(f)
    response = {'images' : imgs, 'videos': videos}

    return response
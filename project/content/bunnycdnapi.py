import requests
import json
from project import cache

pullzone_url = "http://91b52230aa5a5ff.b-cdn.net"

@cache.cached(timeout=600)
def getfromcdn(path):
    url = r"https://storage.bunnycdn.com" + path
    AccessKey = "46aefc84-581b-4624-8bdd3e0cbb15-cc91-47f6"
    headers = {
        "Accept": "application/json",
        "AccessKey": AccessKey
    }
    response = requests.get(url, headers=headers)
    data = json.loads(response.content)
    #for c in data:
    #    if c['IsDirectory']:
    #        print(c['ObjectName'])
    return data

#   Получение каталогов в пути CDN и вывод их в виде словаря
@cache.cached(timeout=600)
def opendir(path="/ap4uklor/"):
    data = getfromcdn(path)
    dirs = {}
    for c in data:
        if c['IsDirectory']:
            dirs[c['ObjectName']] = {"path": c['Path']}

    return dirs


#   Получение списка файлов в пути CDN и вывод их в виде словаря
@cache.cached(timeout=600)
def showfiles(path):

    data = getfromcdn(path)

    files = {}
    for c in data:
        #if c['IsDirectory'] is False:
        files[c['ObjectName']] = {"path": c['Path'], "IsDirectory": c['IsDirectory']}
    print(data)
    print(files)
    return files

@cache.cached(timeout=600)
def filesfromfolder(path="/ap4uklor/"):
    #print("Path в bunnycdn" + path)
    dirfiles = showfiles(path)
    imgs, videos, folders = [], [], []
    for f in dirfiles:
        # Вывод изображений
        if f.lower().endswith(('.png', '.jpg', '.jpeg')) and not f.lower().startswith(('thumbnail', 'face')):
            imgs.append(f)
        # Вывод видеофайлов
        elif f.lower().endswith('.mp4'):
            videos.append(f)
        elif f['IsDirectory']:
            folders.append(f)
    response = {'images' : imgs, 'videos': videos, 'folders': folders}
    return response

def filesfromfolder(path="/ap4uklor/"):
    #print("Path в bunnycdn" + path)
    dirfiles = showfiles(path)
    imgs, videos = [], []
    for f in dirfiles:
        # Вывод изображений
        if f.lower().endswith(('.png', '.jpg', '.jpeg')) and not f.lower().startswith(('thumbnail', 'face')):
            imgs.append(f)
        # Вывод видеофайлов
        elif f.lower().endswith('.mp4'):
            videos.append(f)
    response = {'images' : imgs, 'videos': videos}
    return response
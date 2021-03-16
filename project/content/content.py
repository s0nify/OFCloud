from flask import render_template, Blueprint
from flask_paginate import Pagination, get_page_args
from flask_login import login_required
import requests

content = Blueprint('content', __name__, template_folder='templates')

# Необходимые переменные для запросов с фронтенда
APP_API_BACKEND = "http://135.181.9.250:83"
APP_CDN_BACKEND = "http://135.181.9.250:84"


@content.route("/")
# @login_required
def template_test():
    json_data = requests.get("%s/api/v1/dirs" % APP_API_BACKEND).json()
    dirs_list = {}

    for i in json_data["dirs"]:
        dirs_list[json_data["dirs"][i]["dirname"]] = {"videos": json_data["dirs"][i]["videos"],
                                                      "images": json_data["dirs"][i]["images"]}
    return render_template("content/index.html", dirs="Файлы", dirs_list=dirs_list)


@content.route('/photos/<name>')
@login_required
def my_view_content(name):
    dirs_list = {}
    dirs_list["images"] = []

    json_data1 = requests.get(APP_API_BACKEND + "/api/v1/dir/" + name).json()
    for images in json_data1["images"]:
        dirs_list['images'].append(json_data1["images"][images]['filename'])

    dirs_content = {}
    dirs_content["images"] = []

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')

    per_page = 283
    total = len(dirs_list['images'])
    # Количество отображаемых изображений на странице
    print(len(dirs_list['images']))

    dirs_render = {}
    dirs_render["images"] = []
    offset = (page - 1) * per_page
    dirs_render['images'] = dirs_list['images'][offset: offset + per_page]
    print("Страница: ")
    print(page)
    print("Оффсет: ")
    print(offset)
    pagination = Pagination(page=page, alignment='center', per_page=per_page, total=total,
                            css_framework='bootstrap4')

    return render_template("content/photos.html",
                           folder=name,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           dirs_list=dirs_render
                           )


@content.route('/videos/<name>')
@login_required
def my_view_videos(name):
    dirs_list = {"images": [], "videos": []}

    json_data1 = requests.get(APP_API_BACKEND + "/api/v1/dir/" + name).json()

    for images in json_data1["images"]:
        dirs_list['images'].append(json_data1["images"][images]['filename'])
    for videos in json_data1["videos"]:
        dirs_list['videos'].append(json_data1["videos"][videos]['filename'])

    dirs_content = {}
    dirs_content["images"] = []
    dirs_content["videos"] = []

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total = len(dirs_list['videos'])
    per_page = 9
    dirs_content['videos'] = dirs_list['videos'][offset: offset + per_page]
    pagination = Pagination(page=page, alignment='center', per_page=per_page, total=total,
                            css_framework='bootstrap4')

    return render_template("/content/videos.html",
                           folder=name,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           dirs_list=dirs_content
                           )

from flask import render_template, Blueprint, current_app
from flask_paginate import Pagination, get_page_args
from flask_login import login_required
import requests
from project.content.bunnycdnapi import opendir, filesfromfolder
from project.content.securelink import securepath
content = Blueprint('content', __name__, template_folder='templates')



@content.route("/")
# @login_required
def template_test():
    data = opendir()
    return render_template("content/index.html", data=data)


@content.route('/photos/<name>')
@login_required
def my_view_content(name):
    ## Добавить проверку на наличие имени модели
    path = "/" + name + "/"
    images_from_func = filesfromfolder("/ap4uklor/" + path)['images']
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')

    images = []
    for i in images_from_func:
        fullimage = current_app.config["STATIC_CDN_BACKEND"] + securepath("/fullimg" + path + i)
        thumbimage = current_app.config["STATIC_CDN_BACKEND"] + securepath("/thumbimg" + path + i)
        images.append({ 'fullimage' : fullimage, 'thumbimage' : thumbimage })

    per_page = 30
    total = len(images)
    # Количество отображаемых изображений на странице

    images_paged = {}
    offset = (page - 1) * per_page
    images_paged = images[offset: offset + per_page]

    pagination = Pagination(page=page, alignment='center', per_page=per_page, total=total,
                            css_framework='bootstrap4')

    return render_template("content/photos.html",
                           folder=name,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           images=images_paged,
                           path=path,
                           STATIC_CDN_BACKEND=current_app.config["STATIC_CDN_BACKEND"]
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

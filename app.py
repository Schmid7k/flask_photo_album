from flask import Flask, jsonify, request, Response
from bson import objectid
from database.db import initialize_db
from database.models import Photo, Album
import json
from bson.objectid import ObjectId
import os
import urllib
import base64
import codecs

app = Flask(__name__)

# database configs
app.config["MONGODB_SETTINGS"] = {
    "host": "mongodb://mongo:27017/flask-database"
    #'host':'mongodb://mongo:<port>/<name of db>'
    #'host':'mongodb://localhost/<name of db>'
}
db = initialize_db(app)

## ------
# Helper functions to be used if required
# -------
def str_list_to_objectid(str_list):
    return list(map(lambda str_item: ObjectId(str_item), str_list))


def object_list_as_id_list(obj_list):
    return list(map(lambda obj: str(obj.id), obj_list))


# ----------
# PHOTO APIs
# ----------


@app.route("/listPhoto", methods=["POST"])
def add_photo():
    posted_image = request.files.get("file", "")
    posted_data = request.form.to_dict()
    # Check for default album
    def_albums = Album.objects(name="Default")
    if def_albums is None:
        album = Album(name="Default", description="The default album")
        album.save()
    if "albums" in posted_data:
        for album in posted_data["albums"]:
            album = Album(**album)
            album.save()
        posted_data["albums"] = str_list_to_objectid(
            posted_data["albums"] + ["Default"]
        )
    else:
        default = Album.objects().get(name="Default")
        posted_data["albums"] = [default.id]
    photo = Photo(**posted_data)
    photo.image_file.replace(posted_image)
    photo.save()
    status_code = 201
    output = {"message": "Photo successfully created", "id": str(photo.id)}
    return output, status_code


@app.route("/listPhoto/<photo_id>", methods=["GET", "PUT", "DELETE"])
def get_photo_by_id(photo_id: str):
    if request.method == "GET":
        photo = Photo.objects().get(id=photo_id)
        if photo:
            ## Photos should be encoded with base64 and decoded using UTF-8 in all GET requests with an image before sending the image as shown below
            base64_data = codecs.encode(photo.image_file.read(), "base64")
            image = base64_data.decode("utf-8")
            ##########
            output = {
                "name": photo.name,
                "tags": photo.tags,
                "location": photo.location,
                "albums": object_list_as_id_list(photo.albums),
                "file": image,
            }
            status_code = 200
            return output, status_code
    elif request.method == "PUT":
        photo = Photo.objects().get(id=photo_id)
        body = request.get_json()
        keys = body.keys()
        posted_image = request.files.get("file", "")
        if body and keys and photo:
            if "tags" in keys:
                body["tags"] = body["tags"]
            if "albums" in keys:
                body["albums"] = str_list_to_objectid(body["albums"])
            Photo.objects().get(id=photo_id).update(**body)
            if posted_image:
                Photo.objects().get(id=photo_id).update(image_file=posted_image)
            output = {
                "message": "Photo successfully updated",
                "id": str(photo_id),
            }
            status_code = 200
            return output, status_code
    elif request.method == "DELETE":
        photo = Photo.objects().get(id=photo_id)
        if photo:
            photo.delete()
            output = {"message": "Photo successfully deleted", "id": str(photo_id)}
            status_code = 200
            return output, status_code


@app.route("/listPhotos", methods=["GET"])
def get_photos():
    tag: str = request.args.get("tag")
    albumName: str = request.args.get("albumName")
    photo_objects = []
    if albumName is not None:
        album = Album.objects().get(name=albumName)
        photo_objects = Photo.objects(albums=album)
    elif tag is not None:
        photo_objects = Photo.objects(tags=tag)
    else:
        return "<h1>No query parameters!</h1>"
    photos = []
    for photo in photo_objects:
        ## Photos should be encoded with base64 and decoded using UTF-8 in all GET requests with an image before sending the image as shown below
        base64_data = codecs.encode(photo.image_file.read(), "base64")
        image = base64_data.decode("utf-8")
        ##########
        output = {
            "name": photo.name,
            "location": photo.location,
            "file": image,
        }
        photos.append(output)
    status_code = 200
    return jsonify(photos), status_code


# ----------
# ALBUM APIs
# ----------
@app.route("/listAlbum", methods=["POST"])
def add_album():
    posted_data = request.get_json()
    album = Album(**posted_data)
    album.save()
    status_code = 201
    output = {"message": "Album successfully created", "id": str(album.id)}
    return output, status_code


@app.route("/listAlbum/<album_id>", methods=["GET", "PUT", "DELETE"])
def get_album_by_id(album_id):
    if request.method == "GET":
        album = Album.objects().get(id=album_id)
        if album:
            output = {
                "id": str(album.id),
                "name": album.name,
            }
            status_code = 200
            return output, status_code
    elif request.method == "PUT":
        album = Album.objects().get(id=album_id)
        body = request.get_json()
        keys = body.keys()
        if body and keys and album:
            Album.objects().get(id=album_id).update(**body)
            output = {
                "message": "Album successfully updated",
                "id": str(album_id),
            }
            status_code = 200
            return output, status_code
    elif request.method == "DELETE":
        album = Album.objects().get(id=album_id)
        if album:
            album.delete()
            output = {"message": "Album successfully deleted", "id": str(album_id)}
            status_code = 200
            return output, status_code


# Only for local testing without docker
# app.run() # FLASK_APP=app.py FLASK_ENV=development flask run

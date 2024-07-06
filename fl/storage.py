import enum
import json
import os
import zipfile
from io import BytesIO

import boto3
from dotenv import load_dotenv
from werkzeug.datastructures.file_storage import FileStorage

from fl.models import Quest, User, GeoPoint

load_dotenv()
session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    region_name=os.getenv('YANDEX_DEFAULT_REGION'),
    endpoint_url=os.getenv('YANDEX_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('YANDEX_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('YANDEX_SECRET_KEY')
)

BUCKET_NAME = os.getenv('YANDEX_BUCKET_NAME')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')


def upload_file(file: FileStorage, object_name: str) -> dict:
    try:
        print("erere")
        s3.put_object(Bucket=BUCKET_NAME, Key=object_name, Body=file)
        return {"message": "File uploaded", "status": "success"}
    except Exception as e:
        print(str(e))
        return {"message": str(e), "status": "error"}


def copy_file(object_name: str, to_object: str) -> dict:
    try:
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=object_name)
        s3.put_object(Bucket=BUCKET_NAME, Key=to_object, Body=obj['Body'].read())

        return {"message": "File copied", "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def delete_quest_res(quest: Quest, is_draft: bool = False):
    for_deletion = []

    try:
        link_to_promo = quest.link_to_promo_draft if is_draft else quest.link_to_promo
        if link_to_promo:
            for_deletion.append({'Key': link_to_promo})

        if for_deletion:
            s3.delete_objects(Bucket=BUCKET_NAME, Delete={'Objects': for_deletion})

        return {"message": "Quest deleted", "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def delete_geopoint_res(geopoint: GeoPoint, is_draft: bool = False):
    for_deletion = []
    try:
        if is_draft:
            links = [
                geopoint.link_to_promo_draft,
                geopoint.link_to_audio_draft
            ]
            media_links = geopoint.links_to_media_draft
        else:
            links = [
                geopoint.link_to_promo,
                geopoint.link_to_audio
            ]
            media_links = geopoint.links_to_media

        for link in links:
            if link:
                for_deletion.append({'Key': link})

        if media_links:
            for_deletion.extend({'Key': geo_link} for geo_link in media_links)

        s3.delete_objects(Bucket=BUCKET_NAME, Delete={'Objects': for_deletion})
        return {"message": "Geopoint deleted", "status": "success"}
    except Exception as e:
        print(e)
        return {"message": str(e), "status": "error"}


def load_quests_list(offset: int, limit: int = 5):
    try:
        quests = Quest.query.limit(limit).offset(offset).all()
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_ref:
            for quest in quests:
                ans = load_quest(quest, is_draft=False, add_author=True)
                if ans['status'] == 'success':
                    ans = ans['message']
                    for path, content in ans['files']:
                        path = path.split('/', 2)[-1]
                        zip_ref.writestr(f'{quest.id}/{path}', content)
                    zip_ref.writestr(f'{quest.id}/data.json', ans['data'])
                else:
                    raise Exception(ans['message'])
        zip_buffer.seek(0)
        return {"message": zip_buffer, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def load_quest_geopoint(quest: Quest, is_draft: bool = False):
    try:
        geopoints = quest.geopoints
        if is_draft:
            geopoints.extend(quest.geopoints_draft)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_ref:
            for geopoint in geopoints:
                ans = load_geopoint(geopoint, is_draft=is_draft)
                if ans['status'] == 'success':
                    ans = ans['message']
                    for path, content in ans['files']:
                        path = path.split('/', 1)[-1]
                        zip_ref.writestr(f'{geopoint.id}/{path}', content)
                    zip_ref.writestr(f'{geopoint.id}/data.json', ans['data'])
                else:
                    raise Exception(ans['message'])
        zip_buffer.seek(0)
        return {"message": zip_buffer, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def load_user_geopoint(user_id: int, is_draft: bool = True):
    try:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_ref:
            geopoints = User.query.get(user_id).geo_points
            for geo in geopoints:
                ans = load_geopoint(geo, is_draft=is_draft)
                if ans['status'] == 'success':
                    ans = ans['message']
                    for path, content in ans['files']:
                        path = path.split('/', 2)[-1]
                        zip_ref.writestr(f'{geo.id}/{path}', content)
                    zip_ref.writestr(f'{geo.id}/data.json', ans['data'])

        zip_buffer.seek(0)
        return {"message": zip_buffer, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def load_geopoints_list(offset: int, limit: int = 5):
    files_to_upload = []
    # json_data = {}
    try:
        quests = Quest.query.filter_by(published=True).offset(offset).limit(limit).all()
        for quest in quests:
            # add quest promo
            # files_to_upload.append(quest.link_to_promo)

            # add user logo
            files_to_upload.append(User.query.get(quest.user_id).link_to_profile_picture)
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_ref:
            for quest, s3_object_name in zip(quests, files_to_upload):
                rsp = s3.get_object(Bucket=BUCKET_NAME, Key=s3_object_name)
                zip_ref.writestr(f'{quest.id}/{s3_object_name}', rsp['Body'].read())
                json_data = {
                    "quest_id": quest.id,
                    "title": quest.title,
                    "description": quest.description,
                    "rating": quest.rating,
                    "rating_count": quest.rating_count,
                    "author_name": User.query.get(quest.user_id).username,
                }

                json_bytes = json.dumps(json_data).encode('utf-8')
                zip_ref.writestr(f'{quest.id}/data.json', json_bytes)

        zip_buffer.seek(0)
        return {"message": zip_buffer, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def load_quest(quest: Quest, is_draft: bool = False, add_author: bool = False):
    getting_files = []
    ans = {
        "data": {},
        "files": []
    }

    try:
        if quest.link_to_promo:
            getting_files.append(quest.link_to_promo)

        if is_draft and quest.link_to_promo_draft:
            getting_files.append(quest.link_to_promo_draft)

        if add_author:
            getting_files.append(User.query.get(quest.user_id).link_to_profile_picture)

        for s3_object_name in getting_files:
            rsp = s3.get_object(Bucket=BUCKET_NAME, Key=s3_object_name)
            ans["files"].append((s3_object_name, rsp['Body'].read()))

        json_data = {
            "quest_id": quest.id,
            "title": quest.title,
            "description": quest.description,
            "geopoints": quest.geopoints
        }
        if is_draft:
            json_data["title_draft"] = quest.title_draft
            json_data["description_draft"] = quest.description_draft
            json_data["geopoints_draft"] = quest.geopoints_draft

        if add_author:
            json_data['rating'] = quest.rating
            json_data['rating_count'] = quest.rating_count
            json_data["author_name"] = User.query.get(quest.user_id).username

        ans["data"] = json.dumps(json_data).encode('utf-8')

        return {"message": ans, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def load_geopoint(geopoint: GeoPoint, is_draft: bool = False, add_author: bool = False):
    getting_files = []
    ans = {
        "data": {},
        "files": []
    }

    try:
        if geopoint.link_to_promo:
            getting_files.append(geopoint.link_to_promo)

        if geopoint.links_to_media:
            getting_files.extend(geopoint.links_to_media)

        if geopoint.link_to_audio:
            getting_files.extend(geopoint.link_to_audio)

        if is_draft and geopoint.link_to_promo_draft:
            getting_files.append(geopoint.link_to_promo_draft)

        if is_draft and geopoint.links_to_media_draft:
            getting_files.extend(geopoint.links_to_media_draft)

        if is_draft and geopoint.link_to_audio_draft:
            getting_files.append(geopoint.link_to_audio_draft)

        if add_author:
            getting_files.append(User.query.get(geopoint.user_id).link_to_profile_picture)

        for s3_object_name in getting_files:
            rsp = s3.get_object(Bucket=BUCKET_NAME, Key=s3_object_name)
            ans["files"].append((s3_object_name, rsp['Body'].read()))

        json_data = {
            "geopoint_id": geopoint.id,
            "title": geopoint.title,
            "coords": geopoint.coords,
            "description": geopoint.description
        }
        if is_draft:
            json_data["title_draft"] = geopoint.title_draft
            json_data["coords_draft"] = geopoint.coords_draft
            json_data["description_draft"] = geopoint.description_draft

        if add_author:
            json_data["author_name"] = User.query.get(geopoint.user_id).username

        ans["data"] = json.dumps(json_data).encode('utf-8')

        return {"message": ans, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}

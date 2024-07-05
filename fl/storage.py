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
        path = os.path.join(UPLOAD_FOLDER, object_name)
        file.save(path)
        s3.upload_file(path, BUCKET_NAME, object_name)
        os.remove(path)
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
        return {"message": str(e), "status": "error"}


def load_quest_for_edit(quest: Quest):
    files_to_upload = []
    try:
        if quest.link_to_promo:
            files_to_upload.append(quest.link_to_promo)

        if quest.link_to_promo_draft:
            files_to_upload.append(quest.link_to_promo_draft)
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_ref:
            for s3_object_name in files_to_upload:
                rsp = s3.get_object(Bucket=BUCKET_NAME, Key=s3_object_name)
                zip_ref.writestr(f'{quest.id}/{s3_object_name}', rsp['Body'].read())

            json_data = {"quest_id": quest.id,
                         "title": quest.title,
                         "description": quest.description,
                         "geopoints": quest.geopoints,
                         "title_draft": quest.title_draft,
                         "description_draft": quest.description_draft,
                         "geopoints_draft": quest.geopoints_draft, }
            json_bytes = json.dumps(json_data).encode('utf-8')
            zip_ref.writestr(f'{quest.id}/data.json', json_bytes)

        zip_buffer.seek(0)

        return {"message": zip_buffer, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def load_geopoint_for_edit(geopoint: GeoPoint):
    files_to_upload = []
    try:
        if geopoint.link_to_promo:
            files_to_upload.append(geopoint.link_to_promo)
        if geopoint.link_to_promo_draft:
            files_to_upload.append(geopoint.link_to_promo_draft)

        if geopoint.link_to_audio:
            files_to_upload.append(geopoint.link_to_audio)
        if geopoint.link_to_audio_draft:
            files_to_upload.append(geopoint.link_to_audio_draft)

        if len(geopoint.link_to_media_draft) > 0:
            files_to_upload.extend(geopoint.link_to_media_draft)
        if len(geopoint.link_to_media) > 0:
            files_to_upload.extend(geopoint.link_to_media)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_ref:
            for s3_object_name in files_to_upload:
                rsp = s3.get_object(Bucket=BUCKET_NAME, Key=s3_object_name)
                zip_ref.writestr(f'{geopoint.id}/{s3_object_name}', rsp['Body'].read())

            json_data = {"quest_id": geopoint.id,
                         "title": geopoint.title,
                         "cords": geopoint.cords,
                         "description": geopoint.description,
                         "title_draft": geopoint.title_draft,
                         "cords_draft": geopoint.coords_draft,
                         "description_draft": geopoint.description_draft,
                         }
            json_bytes = json.dumps(json_data).encode('utf-8')
            zip_ref.writestr(f'{geopoint.id}/data.json', json_bytes)

        zip_buffer.seek(0)

        return {"message": zip_buffer, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def load_quest_for_view(quest: Quest):
    files_to_upload = []

    try:
        files_to_upload.append(quest.link_to_promo)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_ref:
            for s3_object_name in files_to_upload:
                rsp = s3.get_object(Bucket=BUCKET_NAME, Key=s3_object_name)
                zip_ref.writestr(f'{quest.id}/{s3_object_name}', rsp['Body'].read())

            json_data = {"quest_id": quest.id,
                         "title": quest.title,
                         "description": quest.description,
                         "geopoints": quest.geopoints}
            json_bytes = json.dumps(json_data).encode('utf-8')
            zip_ref.writestr(f'{quest.id}/data.json', json_bytes)

        zip_buffer.seek(0)

        return {"message": zip_buffer, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def load_geopoint_for_view(geopoint: GeoPoint):
    files_to_upload = []
    try:
        files_to_upload.append(geopoint.link_to_promo)
        files_to_upload.append(geopoint.link_to_audio)
        files_to_upload.extend(geopoint.link_to_media)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_ref:
            for s3_object_name in files_to_upload:
                rsp = s3.get_object(Bucket=BUCKET_NAME, Key=s3_object_name)
                zip_ref.writestr(f'{geopoint.id}/{s3_object_name}', rsp['Body'].read())

            json_data = {"quest_id": geopoint.id,
                         "title": geopoint.title,
                         "cords": geopoint.cords,
                         "description": geopoint.description,
                         }
            json_bytes = json.dumps(json_data).encode('utf-8')
            zip_ref.writestr(f'{geopoint.id}/data.json', json_bytes)

        zip_buffer.seek(0)

        return {"message": zip_buffer, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def load_quests_list(offset: int, limit: int = 5):
    files_to_upload = []
    # json_data = {}
    try:
        quests = Quest.query.offset(offset).limit(limit).all()
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

def load_geopoints_list(offset: int, limit: int = 5):
    files_to_upload = []
    # json_data = {}
    try:
        quests = Quest.query.offset(offset).limit(limit).all()
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


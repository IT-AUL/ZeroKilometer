import json
import os
import zipfile
from io import BytesIO

import boto3
from dotenv import load_dotenv
from werkzeug.datastructures.file_storage import FileStorage

from fl.models import Quest, User

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
        return {"message": str(e), "status": "error"}


def delete_quest_res(quest: Quest, is_draft: bool = False):
    for_deletion = []
    try:
        if is_draft:
            if quest.link_to_promo_draft:
                for_deletion.append({'Key': quest.link_to_promo_draft})
            s3.delete_objects(Bucket=BUCKET_NAME, Delete={'Objects': for_deletion})
        else:
            if quest.link_to_promo:
                for_deletion.append({'Key': quest.link_to_promo})
            s3.delete_objects(Bucket=BUCKET_NAME, Delete={'Objects': for_deletion})
        return {"message": "Quest deleted", "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def load_quest_for_edit(quest: Quest):
    files_to_upload = []

    try:
        if quest.link_to_promo:
            local_path = os.path.join(UPLOAD_FOLDER, quest.link_to_promo)
            files_to_upload.append((local_path, quest.link_to_promo))

        if quest.link_to_promo_draft:
            local_path = os.path.join(UPLOAD_FOLDER, quest.link_to_promo_draft)
            files_to_upload.append((local_path, quest.link_to_promo_draft))
        print(files_to_upload)
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_ref:
            for local_path, s3_object_name in files_to_upload:
                print(local_path, s3_object_name)
                rsp = s3.get_object(Bucket=BUCKET_NAME, Key=s3_object_name)
                zip_ref.writestr(s3_object_name, rsp['Body'].read())
                # s3.get_object(local_path, BUCKET_NAME, s3_object_name)
                print("egegeg")
                # zip_ref.write(local_path, s3_object_name)
                print("qqq")
                # os.remove(local_path)
                print("yyy")
            json_data = {"quest_id": quest.id,
                         "title": quest.title,
                         "description": quest.description,
                         "geopoints": quest.geopoints,
                         "title_draft": quest.title_draft,
                         "description_draft": quest.description_draft,
                         "geopoints_draft": quest.geopoints_draft, }
            json_bytes = json.dumps(json_data).encode('utf-8')
            zip_ref.writestr('data.json', json_bytes)

        zip_buffer.seek(0)

        return {"message": zip_buffer, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def load_quest_for_view(quest: Quest):
    files_to_upload = []

    try:
        local_path = os.path.join(UPLOAD_FOLDER, quest.link_to_promo)
        files_to_upload.append((local_path, quest.link_to_promo))

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_ref:
            for local_path, s3_object_name in files_to_upload:
                s3.upload_file(local_path, BUCKET_NAME, s3_object_name)
                zip_ref.write(local_path, s3_object_name)
                os.remove(local_path)
            json_data = {"quest_id": quest.id,
                         "title": quest.title,
                         "description": quest.description,
                         "geopoints": quest.geopoints}
            json_bytes = json.dumps(json_data).encode('utf-8')
            zip_ref.writestr('data.json', json_bytes)

        zip_buffer.seek(0)

        return {"message": zip_buffer, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def load_quests_list(offset: int, limit: int = 5):
    files_to_upload = []
    json_data = {}
    try:
        quests = Quest.query.offset(offset).limit(limit).all()
        for quest in quests:
            json_data[quest.id] = {
                "title": quest.title,
                "description": quest.description,
                "rating": quest.rating,
                "rating_count": quest.rating_count,
                "author_name": User.query.get(quest.user_id).username,
            }
            # add quest promo
            # local_path = os.path.join(UPLOAD_FOLDER, quest.link_to_promo)
            # files_to_upload.append((local_path, quest.link_to_promo))

            # add user logo

            # local_path = os.path.join(UPLOAD_FOLDER, User.query.get(quest.user_id).link_to_profile_picture)
            # files_to_upload.append((local_path, User.query.get(quest.user_id).link_to_profile_picture))
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_ref:
            for local_path, s3_object_name in files_to_upload:
                s3.upload_file(local_path, BUCKET_NAME, s3_object_name)
                zip_ref.write(local_path, s3_object_name)
                os.remove(local_path)
            print(json_data)
            json_bytes = json.dumps(json_data).encode('utf-8')
            zip_ref.writestr('data.json', json_bytes)

        zip_buffer.seek(0)
        return {"message": zip_buffer, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}

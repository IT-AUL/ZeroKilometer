import enum
import json
import os
import zipfile
from io import BytesIO

import boto3
from dotenv import load_dotenv

from fl.models import Quest, User, Location

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


def upload_file(file, object_name: str) -> dict:
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=object_name, Body=file)
        return {"message": "File uploaded", "status": "success"}
    except Exception as e:
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
        link_to_audio = quest.link_to_audio_draft if is_draft else quest.link_to_audio

        if link_to_promo:
            for_deletion.append({'Key': link_to_promo})
        if link_to_audio:
            for_deletion.append({'Key': link_to_audio})

        if for_deletion:
            s3.delete_objects(Bucket=BUCKET_NAME, Delete={'Objects': for_deletion})

        return {"message": "Quest deleted", "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def delete_location_res(location: Location, is_draft: bool = False):
    for_deletion = []
    try:
        if is_draft:
            links = [
                location.link_to_promo_draft,
                location.link_to_audio_draft
            ]
            media_links = location.links_to_media_draft
        else:
            links = [
                location.link_to_promo,
                location.link_to_audio
            ]
            media_links = location.links_to_media

        for link in links:
            if link:
                for_deletion.append({'Key': link})

        if media_links:
            for_deletion.extend({'Key': loc_link} for loc_link in media_links)

        s3.delete_objects(Bucket=BUCKET_NAME, Delete={'Objects': for_deletion})
        return {"message": "Location's res deleted", "status": "success"}
    except Exception as e:
        print(e)
        return {"message": str(e), "status": "error"}


def load_quests_list(offset: int, limit: int = 5):
    try:
        quests = Quest.query.filter_by(published=True).offset(offset).limit(limit).all()
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


def load_quest_locations(quest: Quest, is_draft: bool = False):
    try:
        locations = quest.locations
        if is_draft:
            locations.extend(quest.locations_draft)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_ref:
            for loc in locations:
                ans = load_location(loc, is_draft=is_draft)
                if ans['status'] == 'success':
                    ans = ans['message']
                    for path, content in ans['files']:
                        path = path.split('/', 1)[-1]
                        zip_ref.writestr(f'{loc.id}/{path}', content)
                    zip_ref.writestr(f'{loc.id}/data.json', ans['data'])
                else:
                    raise Exception(ans['message'])
        zip_buffer.seek(0)
        return {"message": zip_buffer, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def load_user_locations(user_id: int, is_draft: bool = True):
    try:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_ref:
            locations = User.query.get(user_id).locations
            for loc in locations:
                ans = load_location(loc, is_draft=is_draft)
                if ans['status'] == 'success':
                    ans = ans['message']
                    for path, content in ans['files']:
                        path = path.split('/', 2)[-1]
                        zip_ref.writestr(f'{loc.id}/{path}', content)
                    zip_ref.writestr(f'{loc.id}/data.json', ans['data'])

        zip_buffer.seek(0)
        return {"message": zip_buffer, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def load_user_quests(user_id: int, is_draft: bool = True):
    try:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_ref:
            quests = User.query.get(user_id).quests
            for que in quests:
                ans = load_quest(que, is_draft=is_draft)
                if ans['status'] == 'success':
                    ans = ans['message']
                    for path, content in ans['files']:
                        path = path.split('/', 2)[-1]
                        zip_ref.writestr(f'{que.id}/{path}', content)
                    zip_ref.writestr(f'{que.id}/data.json', ans['data'])

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

        if quest.link_to_audio:
            getting_files.append(quest.link_to_audio)

        if is_draft and quest.link_to_promo_draft:
            getting_files.append(quest.link_to_promo_draft)

        if is_draft and quest.link_to_audio_draft:
            getting_files.append(quest.link_to_audio_draft)

        if add_author:
            getting_files.append(User.query.get(quest.user_id).link_to_profile_picture)

        for s3_object_name in getting_files:
            rsp = s3.get_object(Bucket=BUCKET_NAME, Key=s3_object_name)
            ans["files"].append((s3_object_name, rsp['Body'].read()))

        json_data = {
            "quest_id": quest.id,
            "title": quest.title,
            "description": quest.description,
            "locations": [loc.id for loc in quest.locations]
        }
        if is_draft:
            json_data["title_draft"] = quest.title_draft
            json_data["description_draft"] = quest.description_draft
            json_data["locations_draft"] = [loc.id for loc in quest.locations_draft]
        if add_author:
            json_data['rating'] = quest.rating
            json_data['rating_count'] = quest.rating_count
            json_data["author_name"] = User.query.get(quest.user_id).username
        ans["data"] = json.dumps(json_data).encode('utf-8')
        return {"message": ans, "status": "success"}

    except Exception as e:
        print(str(e))
        return {"message": str(e), "status": "error"}


def load_location(location: Location, is_draft: bool = False, add_author: bool = False):
    getting_files = []
    ans = {
        "data": {},
        "files": []
    }

    try:
        if location.link_to_promo:
            getting_files.append(location.link_to_promo)

        if location.links_to_media:
            getting_files.extend(location.links_to_media)

        if location.link_to_audio:
            getting_files.extend(location.link_to_audio)

        if is_draft and location.link_to_promo_draft:
            getting_files.append(location.link_to_promo_draft)

        if is_draft and location.links_to_media_draft:
            getting_files.extend(location.links_to_media_draft)

        if is_draft and location.link_to_audio_draft:
            getting_files.append(location.link_to_audio_draft)

        if add_author:
            getting_files.append(User.query.get(location.user_id).link_to_profile_picture)

        for s3_object_name in getting_files:
            rsp = s3.get_object(Bucket=BUCKET_NAME, Key=s3_object_name)
            ans["files"].append((s3_object_name, rsp['Body'].read()))

        json_data = {
            "location_id": location.id,
            "title": location.title,
            "coords": location.coords,
            "description": location.description
        }
        if is_draft:
            json_data["title_draft"] = location.title_draft
            json_data["coords_draft"] = location.coords_draft
            json_data["description_draft"] = location.description_draft

        if add_author:
            json_data["author_name"] = User.query.get(location.user_id).username

        ans["data"] = json.dumps(json_data).encode('utf-8')

        return {"message": ans, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def load_quest_file(quest, is_draft: bool, add_author: bool):
    try:
        ans = load_quest(quest, is_draft, add_author)
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_ref:
            if ans['status'] == 'success':
                ans = ans['message']
                for path, content in ans['files']:
                    path = path.split('/', 2)[-1]
                    zip_ref.writestr(f'{quest.id}/{path}', content)
                zip_ref.writestr(f'{quest.id}/data.json', ans['data'])

        zip_buffer.seek(0)
        return {"message": zip_buffer, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}

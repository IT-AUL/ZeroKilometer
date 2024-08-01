import os
from datetime import datetime, timedelta
from io import BytesIO

from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip
from pydub import AudioSegment
import moviepy.editor as mp
from dotenv import load_dotenv
import hashlib
import hmac
import json
from operator import itemgetter
from urllib.parse import parse_qsl

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


def is_file_allowed(filename, allowed_extensions):
    return (filename != '') and '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions


def convert_image_to_webp(image):
    image = Image.open(image)
    webp_image = BytesIO()
    image.save(webp_image, format='WEBP')
    webp_image.seek(0)
    return webp_image


def convert_audio_to_aac(audio):
    audio_segment = AudioSegment.from_file(audio)
    aac_audio = BytesIO()
    audio_segment.export(aac_audio, format='adts')  # Use 'adts' for AAC
    aac_audio.seek(0)
    return aac_audio


#
# def convert_video_to_webm(video):
#     video = mp.VideoFileClip(video)
#     webm_video = BytesIO()
#     video.write_videofile(webm_video, codec='libvpx', audio_codec='libvorbis')
#     webm_video.seek(0)
#     return webm_video

# def convert_video_to_webm(video):
#     video_bytes = BytesIO()
#     video.save(video_bytes)
#     video_bytes.seek(0)
#     video_clip = mp.VideoFileClip(video_bytes)
#     webm_video = BytesIO()
#     video_clip.write_videofile(webm_video.name, codec='libvpx', audio_codec='libvorbis')
#     webm_video.seek(0)
#     return webm_video


def convert_video_to_webm(file):
    file_stream = BytesIO(file.read())
    file_stream.seek(0)

    # Convert video to WebM format
    input_video = VideoFileClip(file_stream)
    webm_video = BytesIO()
    input_video.write_videofile(webm_video, codec='libvpx', format='webm')
    webm_video.seek(0)
    return webm_video


def is_user_valid(token: str, init_data: str):
    try:
        parsed_data = dict(parse_qsl(init_data))
    except ValueError:
        return False, None
    try:
        user_data = json.loads(parsed_data['user'])
    except (ValueError, KeyError):
        return False, None
    if "hash" not in parsed_data:
        return False, None
    hash_ = parsed_data.pop('hash')
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items(), key=itemgetter(0))
    )
    secret_key = hmac.new(
        key=b"WebAppData", msg=token.encode(), digestmod=hashlib.sha256
    )
    calculated_hash = hmac.new(
        key=secret_key.digest(), msg=data_check_string.encode(), digestmod=hashlib.sha256
    ).hexdigest()
    return calculated_hash == hash_, user_data


def check_telegram_authorization(token, auth_data):
    check_hash = auth_data.pop('hash')
    data_check_arr = []
    for key, value in sorted(auth_data.items()):
        data_check_arr.append(f'{key}={value}')
    data_check_string = '\n'.join(data_check_arr)
    secret_key = hashlib.sha256(token.encode()).digest()
    hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if hash != check_hash:
        return None, False
    auth_date = datetime.fromtimestamp(int(auth_data['auth_date']))
    if datetime.now() - auth_date > timedelta(days=15):
        return None, False
    return auth_data, True

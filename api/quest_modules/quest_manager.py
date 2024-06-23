import json

from api.quest_modules.chapter import Chapter
from api.quest_modules.choice import Choice
from api.quest_modules.quest import Quest
from api.quest_modules.data import Data


def load_chapters(quests_file='q.json'):
    with open(quests_file, encoding='utf-8') as file:
        data = json.load(file)
        uuid = str(data['uuid'])
        chapters = dict()
        for chapter_json in data['chapters']:
            chapter_id = str(chapter_json["chapter_id"])
            title = str(chapter_json["title"])
            res_path = str(chapter_json["res_path"])
            geo_position = str(chapter_json["geo_position"])
            quests = {}
            for quest_json in chapter_json['quests']:
                quest_id = str(quest_json['quest_id'])
                description = str(quest_json['description'])
                choice = []
                for choice_json in quest_json['choices']:
                    choice_id = str(choice_json['choice_id'])
                    next_id = str(choice_json['next_id'])
                    text = str(choice_json['text'])
                    r_path = str(choice_json['res_path'])
                    conditions = [str(condition) for condition in choice_json['conditions']]
                    result = dict(choice_json['result'])
                    choice.append(Choice(choice_id, next_id, text, r_path, conditions, result))
                quests[quest_id] = Quest(quest_id, description, choice)
            chapters[chapter_id] = Chapter(chapter_id, title, res_path, geo_position, quests)
        return Data(uuid, chapters)

import json
import re

from aiogram.utils.keyboard import InlineKeyboardBuilder

from choice import Choice
from com.hakaton.quest.chapter import Chapter
from player import Player
from quest import Quest


def load_chapters(quests_file):
    with open(quests_file, encoding='utf-8') as file:
        chapters = dict()
        for chapter_json in json.load(file):
            chapter_id = str(chapter_json["chapter_id"])
            title = str(chapter_json["title"])
            video_path = str(chapter_json["video_path"])
            geo_position = str(chapter_json["geo_position"])
            quests = {}
            for quest_json in chapter_json['quests']:
                quest_id = str(quest_json['quest_id'])
                description = str(quest_json['description'])
                choice = []
                for choice_json in quest_json['choices']:
                    choice_id = str(choice_json['choice_id'])
                    to_quest = str(choice_json['to_quest'])
                    text = str(choice_json['text'])
                    v_path = str(choice_json['video_path'])
                    conditions = [str(condition) for condition in choice_json['conditions']]
                    result = dict(choice_json['result'])
                    choice.append(Choice(choice_id, to_quest, text, v_path, conditions, result))
                quests[quest_id] = Quest(quest_id, description, choice)
            chapters[chapter_id] = Chapter(chapter_id, title, video_path, geo_position, quests)
        return chapters


class QuestManager:
    player: Player

    def __init__(self, quests_file='quest.json', player=None):
        self.chapters = load_chapters(quests_file)
        self.current_chapter_id = "ch0"
        self.current_chapter = self.chapters[self.current_chapter_id]
        self.current_quest_id = "q0"
        self.current_quest = self.current_chapter.quests[self.current_quest_id]
        self.current_choices = [choice.choice_id for choice in self.current_quest.choices]
        self.player = player

    def get_current_quest(self):
        self.current_quest = self.current_chapter.quests[self.current_quest_id]
        return self.current_quest.description, self.current_quest.choices

    def get_quest_desc_and_choices(self):
        quest_description, choices = self.get_current_quest()
        quest_description = self.replace_variables(quest_description)
        builder = InlineKeyboardBuilder()
        for choice in choices:
            if choice.conditions is None or len(choice.conditions) == 0 or any(
                    [self.replace_variables_and_evaluate(condition) for condition in choice.conditions]):
                choice.text = self.replace_variables(choice.text)
                data = self.current_chapter_id + ";" + self.current_quest_id + ";" + choice.choice_id
                builder.button(text=choice.text, callback_data=data)
        builder.adjust(1, True)
        self.current_choices = [choice.choice_id for choice in choices]
        return quest_description, builder.as_markup()

    def replace_variables(self, string):
        pattern = r'\$(\w+)'
        matches = re.findall(pattern, string)
        for match in matches:
            if hasattr(self.player, match):
                value = str(getattr(self.player, match))
                string = string.replace(f'${match}', value)
        return string

    def replace_variables_and_evaluate(self, expression):
        pattern = r'\$(\w+)'
        matches = re.findall(pattern, expression)
        for match in matches:
            if hasattr(self.player, match):
                value = str(getattr(self.player, match))
                expression = expression.replace(f'${match}', value)
        return eval(expression)

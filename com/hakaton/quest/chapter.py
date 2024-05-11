class Chapter:
    def __init__(self, chapter_id, title, geo_position, quests):
        self.chapter_id = chapter_id
        self.title = title
        self.geo_position = tuple(map(float, geo_position.split(";")))
        self.quests: dict = quests

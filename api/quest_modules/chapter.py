class Chapter:
    def __init__(self, chapter_id, title, res_path, geo_position, quests):
        self.chapter_id: str = chapter_id
        self.title: str = title
        self.res_path: str = res_path
        self.geo_position: tuple = tuple(map(float, geo_position.split(";")))
        self.quests: dict = quests

class Chapter:
    def __init__(self, chapter_id, title, video_path, geo_position, quests):
        self.chapter_id: str = chapter_id
        self.title: str = title
        self.video_path: str = video_path
        self.geo_position: tuple = tuple(map(float, geo_position.split(";")))
        self.quests: dict = quests

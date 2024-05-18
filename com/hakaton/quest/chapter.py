class Chapter:
    def __init__(self, chapter_id, title, video_path, geo_position, quests):
        self.chapter_id = chapter_id
        self.title = title
        self.video_path = video_path
        self.geo_position = tuple(map(float, geo_position.split(";")))
        self.quests: dict = quests

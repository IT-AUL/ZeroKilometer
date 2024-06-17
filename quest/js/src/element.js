class Choice {
    constructor(choiceId, toQuest, text, videoPath, conditions, result) {
        this.choiceId = choiceId;
        this.toQuest = toQuest;
        this.text = text;
        this.videoPath = videoPath;
        this.conditions = conditions;
        this.result = result;
    }
}

class Quest {
    constructor(questId, description, choices) {
        this.questId = questId;
        this.description = description;
        this.choices = choices;
    }
}

class Chapter {
    constructor(chapterId, title, videoPath, geoPosition, quests) {
        this.chapterId = chapterId;
        this.title = title;
        this.videoPath = videoPath;
        this.geoPosition = geoPosition.split(";").map(parseFloat);
        this.quests = quests;
    }
}

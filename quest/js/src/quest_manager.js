import fs from 'fs';
import path from 'path';

function loadChapters(questsFile = 'q.json') {
    const chapters = {};
    const data = fs.readFileSync(path.resolve(questsFile), 'utf8');
    const chaptersJson = JSON.parse(data);
    chaptersJson.forEach(chapterJson => {
        const chapterId = String(chapterJson.chapter_id);
        const title = String(chapterJson.title);
        const videoPath = String(chapterJson.video_path);
        const geoPosition = String(chapterJson.geo_position);
        const quests = {};
        chapterJson.quests.forEach(questJson => {
            const questId = String(questJson.quest_id);
            const description = String(questJson.description);
            const choices = [];
            questJson.choices.forEach(choiceJson => {
                const choiceId = String(choiceJson.choice_id);
                const toQuest = String(choiceJson.to_quest);
                const text = String(choiceJson.text);
                const vPath = String(choiceJson.video_path);
                const conditions = choiceJson.conditions.map(condition => String(condition));
                const result = {...choiceJson.result};
                choices.push(new Choice(choiceId, toQuest, text, vPath, conditions, result));
            });
            quests[questId] = new Quest(questId, description, choices);
        });
        chapters[chapterId] = new Chapter(chapterId, title, videoPath, geoPosition, quests);
    });
    return chapters;
}

class QuestManager {
    constructor(chapters) {
        this.chapters = chapters;
        this.currentChapterId = "ch0";
        this.currentQuestId = "q0";
        this.player = new Player();
        this.isTalkingWithNpc = false;
    }

    getCurrentQuest() {
        let currentQuest = this.chapters[this.currentChapterId].quests[this.currentQuestId];
        return {description: currentQuest.description, choices: currentQuest.choices};
    }

    getQuestDescAndChoices() {
        let {description, choices} = this.getCurrentQuest();
        let availableChoice = []
        choices.forEach(choice => {
            availableChoice.push({
                text: choice.text,
                data: `${this.currentChapterId};${this.currentQuestId};${choice.choiceId}`
            })
        })
        return {description, availableChoice: availableChoice}
    }
}

export default QuestManager;
import QuestManager from "./js/src/quest_manager.js";
import loadChapters from "./js/src/quest_manager"

let chapters = loadChapters();
let questManager = new QuestManager()
updateButton(questManager.getQuestDescAndChoices())

function updateButton(desc, buttons) {
    console.log("update")
    const choicesContainer = document.getElementById('choice-container');
    const text = document.getElementById("text")
    text.innerText = desc

    buttons.forEach(choice => {
        const button = document.createElement('button');
        button.innerText = choice.text;
        button.setAttribute('data-choice', choice.data);
        button.addEventListener('click', handleChoiceClick);
        choicesContainer.appendChild(button);
    })

    function handleChoiceClick(event) {
        const choiceData = event.target.getAttribute('data-choice');
        console.log(`Вы выбрали: ${choiceData}`);
        questManager.isTalkingWithNpc = false

        let choices = questManager.chapters[questManager.currentChapterId].quests[questManager.currentQuestId].choices

        choices.forEach(choice => {
            let compareData = `${questManager.currentChapterId};${questManager.currentQuestId};${choice.choiceId}`
            if (compareData === choiceData) {
                if (choice.toQuest.startsWith("ch")) {
                    questManager.player.changedLocation = True

                    questManager.currentChapterId = choice.toQuest
                    questManager.currentQuestId = "q0"
                }
            } else {
                questManager.currentQuestId = choice.toQuest

                let {desc, buttons} = questManager.getQuestDescAndChoices()
                updateButton(desc, buttons)
            }
        })
    }
}
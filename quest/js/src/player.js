class Player {
    constructor() {
        this.changedLocation = false;
        this.npc = "";
        this.name = "Алмаз";
        this.deck = [];
        this.willFight = 1;
        this.changed = false;
        this.items = [
            {name: "Булат", id: "1", type: "ally"},
            {name: "Тычкан", id: "13", type: "ally"},
            {name: "Бака", id: "14", type: "ally"}
        ];
    }

    addItems(items = []) {
        this.items.push(items)
    }

    clearOpponents() {
        this.items = this.items.filter(item => item.type === "ally")
    }

    // applyChanges({items = [], clear = "False", willFight = 1} = {}) {
    //     if (clear === "True") {
    //         this.items = this.items.filter(item => item.type === "ally");
    //     }
    //
    //     if (this.willFight === 1) {
    //         this.willFight = willFight;
    //     }
    //
    //     for (const item of items) {
    //         if (!this.items.some(i => i.id === item.id && i.type === "ally")) {
    //             this.items.push(item);
    //         }
    //     }
    //
    //     console.log(this.items);
    // }
}
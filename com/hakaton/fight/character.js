class Character {
    constructor(name, image, damage, defense, accuracy, intelligence, range, energy) {
        this.name = name;
        this.image = image;
        this.damage = damage;
        this.defense = defense;
        this.accuracy = accuracy;
        this.intelligence = intelligence;
        this.range = range;
        this.energy = energy;
    }

    // Method to display character information
    displayInfo() {
        console.log(`Name: ${this.name}`);
        console.log(`Image: ${this.image}`);
        console.log(`Damage: ${this.damage}`);
        console.log(`Defense: ${this.defense}`);
        console.log(`Accuracy: ${this.accuracy}`);
        console.log(`Intelligence: ${this.intelligence}`);
        console.log(`Range: ${this.range}`);
        console.log(`Energy: ${this.energy}`);
    }

    // Method to attack another character
}
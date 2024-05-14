// const listContainer = document.createElement("div");
// listContainer.style.overflowY = "auto";
// listContainer.style.height = "300px";
// listContainer.style.width = "300px";
// document.body.appendChild(listContainer);
// // Create an array of image URLs
// const images = [
//     "img.png",
//     "img.png",
//     "img.png",
//     "img.png",
//     "img.png",
// ];
//
// // Create the scrollable list of images
// const list = document.createElement("ul");
// list.style.listStyle = "none";
// list.style.padding = "0";
// list.style.margin = "0";
// listContainer.appendChild(list);
//
// // Create the images and add them to the list
// images.forEach((image, index) => {
//     const listItem = document.createElement("li");
//     listItem.style.padding = "10px";
//     listItem.style.border = "1px solid #ccc";
//     listItem.style.cursor = "pointer";
//     const img = document.createElement("img");
//     img.src = image;
//     img.style.width = "100%";
//     img.style.height = "100%";
//     img.onclick = () => {
//         if (img.classList.contains("selected")) {
//             img.classList.remove("selected");
//             img.style.filter = "";
//         } else if (document.querySelectorAll(".selected").length < 3) {
//             img.classList.add("selected");
//             img.style.filter = "grayscale(100%)";
//         } else {
//             createNotification("You can only select 3 images!");
//         }
//     };
//     listItem.appendChild(img);
//     list.appendChild(listItem);
// });
//
// // Create a button to confirm the selection
// const confirmButton = document.createElement("button");
// confirmButton.textContent = "Confirm";
// confirmButton.onclick = () => {
//     const selectedImages = document.querySelectorAll(".selected");
//     if (selectedImages.length === 3) {
//         const rowContainer = document.createElement("div");
//         rowContainer.style.display = "flex";
//         rowContainer.style.flexDirection = "row";
//         document.body.appendChild(rowContainer);
//         selectedImages.forEach((img) => {
//             const clonedImg = img.cloneNode(true);
//             clonedImg.style.width = "33%";
//             clonedImg.style.height = "100%";
//             clonedImg.style.margin = "10px";
//             rowContainer.appendChild(clonedImg);
//         });
//         listContainer.remove();
//         confirmButton.remove();
//     } else {
//         createNotification("You must select exactly 3 images!");
//     }
// };
// document.body.appendChild(confirmButton);
//
// // Function to create a notification
// function createNotification(message) {
//     const notification = document.createElement("div");
//     notification.style.position = "fixed"; // Use fixed positioning
//     notification.style.top = "0"; // Set top to 0
//     notification.style.left = "50%";
//     notification.style.transform = "translate(-50%, 0)";
//     notification.style.background = "rgba(255, 255, 255, 0.8)";
//     notification.style.padding = "10px";
//     notification.style.borderRadius = "10px";
//     notification.style.boxShadow = "0px 0px 10px rgba(0, 0, 0, 0.2)";
//     notification.style.zIndex = "1000";
//     notification.textContent = message;
//     document.body.appendChild(notification);
//     notification.style.animation = "floatUp 2s forwards";
//     setTimeout(() => {
//         notification.remove();
//     }, 2000);
// }
//
// // Define the animation
// document.styleSheets[0].insertRule(`
//   @keyframes floatUp {
//     0% {
//       transform: translateY(0);
//       opacity: 1;
//     }
//     100% {
//       transform: translateY(-50px);
//       opacity: 0;
//     }
//   }
// `);
class Card {
    constructor(image, damage, defense, accuracy, intelligence, range, energy) {
        this.image = image;
        this.damage = damage;
        this.defense = defense;
        this.accuracy = accuracy;
        this.intelligence = intelligence;
        this.range = range;
        this.energy = energy;
    }
}

const listContainer = document.createElement("div");
listContainer.style.overflowY = "auto";
listContainer.style.height = "300px";
listContainer.style.width = "300px";
document.body.appendChild(listContainer);

// Create an array of card objects
const cards = [
    new Card("img.png", 10, 5, 0.8, 10, 5, 100),
    new Card("img.png", 15, 3, 0.9, 15, 3, 80),
    new Card("img.png", 12, 4, 0.7, 12, 4, 90),
    new Card("img.png", 18, 2, 0.6, 18, 2, 70),
    new Card("img.png", 20, 1, 0.5, 20, 1, 60),
];

// Create the scrollable list of cards
const list = document.createElement("ul");
list.style.listStyle = "none";
list.style.padding = "0";
list.style.margin = "0";
listContainer.appendChild(list);

// Create the cards and add them to the list
cards.forEach((card) => {
    const listItem = document.createElement("li");
    listItem.style.padding = "10px";
    listItem.style.border = "1px solid #ccc";
    listItem.style.cursor = "pointer";
    const img = document.createElement("img");
    img.src = card.image
    img.style.width = "100%";
    img.style.height = "100%";
    img.onclick = () => {
        if (img.classList.contains("selected")) {
            img.classList.remove("selected");
            img.style.filter = "";
        } else if (document.querySelectorAll(".selected").length < 3) {
            img.classList.add("selected");
            img.style.filter = "grayscale(100%)";
        } else {
            createNotification("You can only select 3 cards!");
        }
    };
    listItem.appendChild(img);
    listItem.card = card; // Associate the Card object with the DOM element
    list.appendChild(listItem);
});

// Create a button to confirm the selection
const confirmButton = document.createElement("button");
confirmButton.textContent = "Confirm";
confirmButton.onclick = () => {
    const selectedCards = document.querySelectorAll(".selected");
    if (selectedCards.length === 3) {
        const rowContainer = document.createElement("div");
        rowContainer.style.display = "flex";
        rowContainer.style.flexDirection = "row";
        document.body.appendChild(rowContainer);
        selectedCards.forEach((card) => {
            const clonedCard = card.cloneNode(true);
            clonedCard.style.width = "33%";
            clonedCard.style.height = "100%";
            clonedCard.style.filter = ""
            clonedCard.style.margin = "10px";
            rowContainer.appendChild(clonedCard);
        });
        listContainer.remove();
        confirmButton.remove();
        printCardProperties(selectedCards);
    } else {
        createNotification("You must select exactly 3 cards!");
    }
};
document.body.appendChild(confirmButton);

// Function to create a notification
function createNotification(message) {
    const notification = document.createElement("div");
    notification.style.position = "absolute";
    notification.style.top = "50%";
    notification.style.left = "50%";
    notification.style.transform = "translate(-50%, -50%)";
    notification.style.background = "rgba(255, 255, 255, 0.8)";
    notification.style.padding = "10px";
    notification.style.borderRadius = "10px";
    notification.style.boxShadow = "0px 0px 10px rgba(0, 0, 0, 0.2)";
    notification.style.zIndex = "1000";
    notification.textContent = message;
    document.body.appendChild(notification);
    notification.style.animation = "floatUp 2s forwards";
    setTimeout(() => {
        notification.remove();
    }, 2000);
}

// Define the animation
document.styleSheets[0].insertRule(`
  @keyframes floatUp {
    0% {
      transform: translateY(0);
      opacity: 1;
    }
    100% {
      transform: translateY(-100px);
      opacity: 0;
    }
  }
`);

// Card class

// Function to print card properties
function printCardProperties(selectedCards) {
    const cardPropertiesContainer = document.createElement("div");
    cardPropertiesContainer.style.display = "flex";
    cardPropertiesContainer.style.flexDirection = "column";
    document.body.appendChild(cardPropertiesContainer);
    selectedCards.forEach((card) => {
        const cardProperties = document.createElement("div");
        cardProperties.textContent = `
      Damage: ${card.parentNode.card.damage}
      Defense: ${card.parentNode.card.defense}
      Accuracy: ${card.parentNode.card.accuracy}
      Intelligence: ${card.parentNode.card.intelligence}
      Range: ${card.parentNode.card.range}
      Energy: ${card.parentNode.card.energy}
    `;
        cardPropertiesContainer.appendChild(cardProperties);
    });
}

// Card class

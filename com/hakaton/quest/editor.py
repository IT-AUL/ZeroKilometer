import tkinter as tk
from tkinter import simpledialog


class QuestEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Quest Editor")

        # Create a frame for the quest list
        self.quest_frame = tk.Frame(self.root)
        self.quest_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a listbox to display quests
        self.quest_list = tk.Listbox(self.quest_frame)
        self.quest_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a frame for the quest details
        self.details_frame = tk.Frame(self.root)
        self.details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create labels and entry for quest details
        self.quest_label = tk.Label(self.details_frame, text="Quest Body:")
        self.quest_label.pack()
        self.quest_body = tk.Entry(self.details_frame)
        self.quest_body.pack()

        self.choice_label = tk.Label(self.details_frame, text="Choices:")
        self.choice_label.pack()
        self.choice_list = tk.Listbox(self.details_frame)
        self.choice_list.pack(fill=tk.BOTH, expand=True)

        # Create a button to add a new quest
        self.add_quest_button = tk.Button(self.details_frame, text="Add Quest", command=self.add_quest)
        self.add_quest_button.pack()

        # Create a button to add a new choice
        self.add_choice_button = tk.Button(self.details_frame, text="Add Choice", command=self.add_choice)
        self.add_choice_button.pack()

        # Create a button to save the quests
        self.save_button = tk.Button(self.details_frame, text="Save Quests", command=self.save_quests)
        self.save_button.pack()

        # List to hold quests and choices
        self.quests = []

    def add_quest(self):
        quest_body = self.quest_body.get()
        if quest_body:
            self.quests.append({'body': quest_body, 'choices': []})
            self.quest_list.insert(tk.END, quest_body)
            self.quest_body.delete(0, tk.END)

    def add_choice(self):
        selected_quest = self.quest_list.curselection()
        if selected_quest:
            choice = simpledialog.askstring("Input", "Enter choice:", parent=self.root)
            if choice:
                quest_index = selected_quest[0]
                self.quests[quest_index]['choices'].append(choice)
                self.choice_list.insert(tk.END, choice)

    def save_quests(self):
        # Here you would implement the logic to save the quests to a file or database
        print("Quests saved:", self.quests)


# Create the main window
root = tk.Tk()
editor = QuestEditor(root)

# Run the application
root.mainloop()

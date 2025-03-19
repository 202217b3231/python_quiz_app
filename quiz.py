import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import random
import pickle
import os

class QuizApp:
    def __init__(self, master, json_file):
        self.master = master
        master.title("Quiz App")

        self.json_file = json_file
        self.questions = self.load_questions()
        self.current_question_index = 0
        self.attempted_questions = 0
        self.answered_questions = []
        self.score = 0

        self.load_previous_attempts()

        # Styling
        self.style = ttk.Style()
        self.style.configure("Correct.TRadiobutton", foreground="green")
        self.style.configure("Incorrect.TRadiobutton", foreground="red")
        self.style.configure("TLabel", font=("Arial", 16), foreground="blue")
        self.style.configure("TButton", font=("Arial", 12), background="lightblue")
        self.style.configure("TRadiobutton", font=("Arial", 16))

        # Create a canvas and a scrollbar
        self.canvas = tk.Canvas(master)
        self.scrollbar = ttk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.question_label = ttk.Label(self.scrollable_frame, text="", wraplength=self.master.winfo_screenwidth() - 100, style="TLabel", anchor="w")
        self.question_label.pack(pady=10, fill="x", expand=True)

        self.option_var = tk.StringVar()
        self.option_buttons = []
        self.create_option_buttons()

        self.button_frame = ttk.Frame(self.scrollable_frame)
        self.button_frame.pack(pady=10, fill="x", expand=True)

        self.submit_button = ttk.Button(self.button_frame, text="Submit", command=self.check_answer, state=tk.DISABLED, style="TButton")
        self.submit_button.pack(side="left", padx=5)

        self.next_button = ttk.Button(self.button_frame, text="Next", command=self.next_question, state=tk.DISABLED, style="TButton")
        self.next_button.pack(side="left", padx=5)

        self.back_button = ttk.Button(self.button_frame, text="Back", command=self.previous_question, state=tk.DISABLED, style="TButton")
        self.back_button.pack(side="left", padx=5)

        self.explanation_label = ttk.Label(self.scrollable_frame, text="", wraplength=self.master.winfo_screenwidth() - 100, style="TLabel", anchor="w")
        self.explanation_label.pack(pady=10, fill="x", expand=True)

        self.progress_label = ttk.Label(self.scrollable_frame, text="", style="TLabel", anchor="w")
        self.progress_label.pack(pady=10, fill="x", expand=True)

        self.restart_button = ttk.Button(self.scrollable_frame, text="Restart", command=self.restart_quiz, style="TButton")
        self.restart_button.pack(pady=10)

        self.load_question()

    def load_questions(self):
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
                random.shuffle(data)  # Shuffle questions
                return data
        except FileNotFoundError:
            print(f"Error: File '{self.json_file}' not found.")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in '{self.json_file}'.")
            return []

    def create_option_buttons(self):
        if not hasattr(self, 'option_frame'):
            self.option_frame = ttk.Frame(self.scrollable_frame)
            self.option_frame.pack(pady=10)

            for i in range(4):  # Assuming 4 options (A, B, C, D)
                button = ttk.Radiobutton(self.option_frame, text="", variable=self.option_var, value="", command=self.enable_submit, style="TRadiobutton")
                button.pack(anchor=tk.W, padx=20)
                self.option_buttons.append(button)

    def load_question(self):
        if self.current_question_index < len(self.questions):
            self.update_progress()
            self.reset_ui()
            question_data = self.questions[self.current_question_index]
            self.question_label.config(text=f"Question {question_data['question_number']}: {question_data['question']}")

            options = question_data['options']
            option_keys = list(options.keys())

            if self.current_question_index > 0:
                self.back_button.config(state=tk.NORMAL)
            else:
                self.back_button.config(state=tk.DISABLED)

            for i, key in enumerate(option_keys):
                self.option_buttons[i].config(text=f"{key}: {options[key]}", value=key, state=tk.NORMAL)
            self.option_var.set("")  # Reset the selected option

        else:
            self.show_final_score()

    def enable_submit(self):
        self.submit_button.config(state=tk.NORMAL)

    def check_answer(self):
        if self.current_question_index not in self.answered_questions:
            self.answered_questions.append(self.current_question_index)
            self.attempted_questions += 1

        self.submit_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.NORMAL)
        question_data = self.questions[self.current_question_index]
        correct_answer = question_data['answer']
        explanation = question_data['explanation']

        selected_answer = self.option_var.get()

        if selected_answer == correct_answer:
            self.score += 1
            self.explanation_label.config(text=f"Correct! Explanation: {explanation}", foreground="green")
        else:
            self.explanation_label.config(text=f"Incorrect. Correct answer: {correct_answer}. Explanation: {explanation}", foreground="red")

        for i, key in enumerate(question_data['options'].keys()):
            if key == correct_answer:
                self.option_buttons[i].config(style="Correct.TRadiobutton")
            elif self.option_var.get() == key:
                self.option_buttons[i].config(style="Incorrect.TRadiobutton")

        self.save_attempts()

    def next_question(self):
        self.current_question_index += 1
        self.load_question()

    def previous_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.load_question()

    def update_progress(self):
        self.progress_label.config(text=f"Attempted: {self.attempted_questions}/{len(self.questions)}")

    def reset_ui(self):
        self.explanation_label.config(text="", foreground="black")

        for button in self.option_buttons:
            button.config(style="TRadiobutton")

        self.submit_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)

    def show_final_score(self):
        self.question_label.config(text=f"Quiz Completed! Your score: {self.score}/{len(self.questions)}")
        for button in self.option_buttons:
            button.pack_forget()
        self.submit_button.pack_forget()
        self.next_button.pack_forget()
        self.explanation_label.pack_forget()
        self.back_button.pack_forget()

    def save_attempts(self):
        with open("attempts.pkl", "wb") as f:
            pickle.dump({
                "current_question_index": self.current_question_index,
                "attempted_questions": self.attempted_questions,
                "answered_questions": self.answered_questions,
                "score": self.score
            }, f)

    def load_previous_attempts(self):
        if os.path.exists("attempts.pkl"):
            with open("attempts.pkl", "rb") as f:
                data = pickle.load(f)
                self.current_question_index = data["current_question_index"]
                self.attempted_questions = data["attempted_questions"]
                self.answered_questions = data["answered_questions"]
                self.score = data["score"]

    def restart_quiz(self):
        self.current_question_index = 0
        self.attempted_questions = 0
        self.answered_questions = []
        self.score = 0
        self.load_question()

# Example usage (assuming you have a 'questions.json' file):
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root, "questions.json")  # Replace 'questions.json' with your file
    root.mainloop()
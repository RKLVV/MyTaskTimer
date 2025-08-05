import tkinter as tk
from tkinter import messagebox
import json
import os
import random

DATA_FILE = "tasks_data.json"

def generate_pastel_color():
    r = random.randint(250, 255)
    g = random.randint(179, 241)
    b = random.randint(71, 215)
    return f'#{r:02x}{g:02x}{b:02x}'

class Task:
    def __init__(self, name, duration_minutes, remaining=None, running=False):
        self.name = name
        self.duration = duration_minutes * 60
        self.remaining = remaining if remaining is not None else self.duration
        self.running = running
        self.timer_id = None

    def to_dict(self):
        return {
            "name": self.name,
            "duration_minutes": self.duration // 60,
            "remaining": self.remaining,
            "running": self.running
        }

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer App")
        theme_bg="#36404A"
        self.root.configure(bg=theme_bg)
        self.root.geometry("400x750")
        self.tasks = []

        top_frame = tk.Frame(root, bg=theme_bg)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        self.user_guide_btn = tk.Button(
            top_frame, text="\u2139", command=self.show_user_guide,
            bg=theme_bg, fg="white", activebackground="#666", activeforeground="white"
        )
        self.user_guide_btn.pack(side=tk.RIGHT)

        self.task_frame = tk.Frame(root, bg=theme_bg)
        self.task_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.no_task_label = tk.Label(
            self.task_frame, text="No tasks for today",
            bg=theme_bg, fg="white", font=("Arial", 14)
        )
        self.no_task_label.pack()

        input_frame = tk.Frame(root, bg=theme_bg)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Task:", bg=theme_bg, fg="white").pack(side=tk.LEFT, padx=5)
        self.task_name_entry = tk.Entry(input_frame, width=20)
        self.task_name_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(input_frame, text="Duration (min):", bg=theme_bg, fg="white").pack(side=tk.LEFT, padx=5)
        self.task_duration_entry = tk.Entry(input_frame, width=5)
        self.task_duration_entry.pack(side=tk.LEFT, padx=5)

        self.add_button = tk.Button(
            input_frame, text="➕", command=self.add_task,
            bg=theme_bg, fg="white", activebackground="#666", activeforeground="white"
        )
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.load_tasks()

    def show_user_guide(self):
        guide_text = (
            "Pomodoro Timer App Guide:\n\n"
            "1. Enter task name and duration in minutes, then click '➕'.\n"
            "2. Each task has buttons to ▶ Start, ⏸ Pause, ⟳ Reset, and ✖ Delete.\n"
            "3. The timer runs in the background and alerts when time is up.\n"
            "4. You can pause or reset the timer anytime.\n"
            "5. Use the 'i' button for help."
        )
        messagebox.showinfo("User Guide", guide_text)

    def save_tasks(self):
        data = [task.to_dict() for task in self.tasks]
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)

    def load_tasks(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                for item in data:
                    task = Task(item["name"], item["duration_minutes"], item["remaining"], item["running"])
                    self.tasks.append(task)
                    self.display_task(task)
                if self.tasks:
                    self.no_task_label.pack_forget()

    def add_task(self):
        name = self.task_name_entry.get().strip()
        duration_text = self.task_duration_entry.get().strip()
        if not name or not duration_text:
            messagebox.showerror("Invalid Input", "Please enter both task name and duration.")
            return
        try:
            minutes = int(duration_text)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for duration.")
            return

        task = Task(name, minutes)
        self.tasks.append(task)
        self.display_task(task)
        self.no_task_label.pack_forget()
        self.task_name_entry.delete(0, tk.END)
        self.task_duration_entry.delete(0, tk.END)
        self.save_tasks()

    def display_task(self, task):
        bg_color = generate_pastel_color()
        #bg_color = "#fa8b50"
        bg_btn = "#4A4A4A"
        fg_btn = "#F7D9BC"
        frame = tk.Frame(self.task_frame, bd=2, relief=tk.RAISED, bg=bg_color)
        frame.pack(fill=tk.X, pady=5)

        name_label = tk.Label(frame, text=task.name, bg=bg_color, fg="#0a0014", font=("Roboto", 13, "bold"))
        name_label.pack(side=tk.LEFT, padx=10)

        time_label = tk.Label(
            frame, text=self.format_time(task.remaining),
            bg=bg_color, fg="#0a0014", font=("Monoid", 14, "bold")
        )
        time_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        button_frame = tk.Frame(frame, bg=bg_color)
        button_frame.pack(side=tk.RIGHT, padx=5)

        start_btn = tk.Button(button_frame, text="\u23F5", bg=bg_btn, fg=fg_btn, width=3)
        start_btn.pack(side=tk.LEFT)
        start_btn.config(command=lambda: self.start_timer(task, time_label, start_btn))

        pause_btn = tk.Button(button_frame, text="\u23F8", command=lambda: self.pause_timer(task, start_btn),
                              bg=bg_btn, fg=fg_btn, width=3)
        pause_btn.pack(side=tk.LEFT)

        reset_btn = tk.Button(button_frame, text="⟳", command=lambda: self.reset_timer(task, time_label, start_btn),
                              bg=bg_btn, fg=fg_btn, width=3)
        reset_btn.pack(side=tk.LEFT)

        delete_btn = tk.Button(button_frame, text="✖", command=lambda: self.delete_task(task, frame),
                               bg=bg_btn, fg="#ff9f9f", width=3)
        delete_btn.pack(side=tk.LEFT)

    def format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02}:{secs:02}"

    def start_timer(self, task, label, start_btn):
        if not task.running and task.remaining > 0:
            task.running = True
            start_btn.config(relief=tk.SUNKEN, fg="#80EF80")
            self.update_timer(task, label, start_btn)

    def update_timer(self, task, label, start_btn):
        if task.remaining > 0 and task.running:
            task.remaining -= 1
            label.config(text=self.format_time(task.remaining))
            task.timer_id = self.root.after(1000, lambda: self.update_timer(task, label, start_btn))
        else:
            task.running = False
            start_btn.config(relief=tk.RAISED)
            self.save_tasks()
            if task.remaining == 0:
                messagebox.showinfo("Time's up!", f"Task '{task.name}' is complete!")

    def pause_timer(self, task, start_btn):
        if task.running:
            task.running = False
            if start_btn:
                start_btn.config(relief=tk.RAISED, fg="#F7D9BC")
            if task.timer_id:
                self.root.after_cancel(task.timer_id)
            self.save_tasks()

    def reset_timer(self, task, label, start_btn):
        self.pause_timer(task, start_btn)
        task.remaining = task.duration
        label.config(text=self.format_time(task.remaining))
        self.save_tasks()

    def delete_task(self, task, frame):
        self.pause_timer(task, None)
        self.tasks.remove(task)
        frame.destroy()
        self.save_tasks()
        if not self.tasks:
            self.no_task_label.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()

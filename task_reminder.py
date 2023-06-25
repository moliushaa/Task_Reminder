import tkinter as tk
from datetime import datetime

task_name = None


def run_countdown():
    def exit_countdown():
        full_screen.destroy()

    def update_countdown():
        now = datetime.now()
        time_left = finish_time - now
        if time_left.total_seconds() <= 0:
            countdown_label.config(text="已截止！")
        else:
            days_left = time_left.days + 1
            countdown_label.config(text=f"{days_left}天！")

        countdown_label.after(1000, update_countdown)

    # Create the running window
    full_screen = tk.Tk()
    full_screen.title("run")
    full_screen.configure(bg="black")
    full_screen.attributes("-fullscreen", True)
    name_label = tk.Label(full_screen, text=f"距离{task_name}还剩:", font=("Arial", 48), fg="white", bg="black")
    name_label.pack(pady=20)
    countdown_label = tk.Label(full_screen, text="好多天！", font=("Arial", 56), fg="white", bg="black")
    countdown_label.pack(pady=20)
    update_countdown()

    # Bind keypress events
    full_screen.bind("<KeyPress-Escape>", lambda event: exit_countdown())
    full_screen.mainloop()


def set_task_name():
    global task_name
    task_name = entry_task_name.get()
    task_name_label.config(text=f"事件名：{entry_task_name.get()}")


def set_finish_time():
    global finish_time
    task_date_label.config(text=f"事件截止日期：{entry_finish_time.get()}")
    finish_time = datetime.strptime(entry_finish_time.get(), "%m/%d/%Y")


# Create the main window
window = tk.Tk()
window.title("Task Reminder")
# window.attributes("-fullscreen", True)
window.geometry("1500x1000")
window.configure(bg="black")

# Create to set task name
task_name_label = tk.Label(window, text='请输入事件名：', font=("Arial", 24), fg="white", bg="black")
task_name_label.pack(pady=20)
entry_task_name = tk.Entry(window, font=("Arial", 24))
entry_task_name.pack(pady=20)
task_name_button = tk.Button(window, text="确认", font=("Arial", 24), command=set_task_name)
task_name_button.pack(pady=20)

# Create the countdown label
task_date_label = tk.Label(window, text="请输入事件截止日期(mm/dd/yyyy)：", font=("Arial", 24), fg="white", bg="black")
task_date_label.pack(pady=20)

# Create the entry field for finish time
entry_finish_time = tk.Entry(window, font=("Arial", 24))
entry_finish_time.pack(pady=20)

# Create the button to set the finish time
set_time_button = tk.Button(window, text="确认", font=("Arial", 24), command=set_finish_time)
set_time_button.pack(pady=20)

# Create the button to run the program
run_button = tk.Button(window, text="开始运行", font=("Arial", 24), command=run_countdown)
run_button.pack(pady=20)

# Start the countdown
finish_time = datetime.now()

# Run the application
window.mainloop()

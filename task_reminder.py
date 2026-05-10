import math
import random
import tkinter as tk
from datetime import datetime, timedelta


class TaskReminderApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.theme = {
            "bg": "#07111f",
            "panel": "#0d1728",
            "panel_alt": "#13233a",
            "line": "#24324a",
            "text": "#f6f7fb",
            "muted": "#9cadc8",
            "accent": "#7bc8ff",
            "accent_alt": "#ffcc66",
            "success": "#56e39f",
            "warning": "#ffc96b",
            "danger": "#ff6b6b",
        }
        self.quotes = [
            "先开始 10 分钟，拖延就会少一半。",
            "别等状态好了才行动，行动本身就是状态。",
            "每天推进一点点，最后会推得很远。",
            "把今天做完，比把明天想完更重要。",
            "你需要的不是完美计划，而是稳定执行。",
            "真正的进步，来自重复的微小胜利。",
        ]

        self.task_name = "你的目标"
        self.note_text = "先完成最难的一步。"
        self.start_time = datetime.now()
        self.deadline = datetime.now() + timedelta(days=30)
        self.last_quote_bucket = None
        self.is_fullscreen = False
        self.card_window = None
        self.card = None
        self.orbs = []

        self.root.title("Task Reminder")
        self.root.geometry("1280x800")
        self.root.minsize(1100, 700)
        self.root.configure(bg=self.theme["bg"])
        self.root.bind("<Escape>", lambda _event: self.exit_app())
        self.root.bind("<F11>", lambda _event: self.toggle_fullscreen())
        # keyboard shortcuts: Enter starts the dashboard, Ctrl+S also starts
        self.root.bind("<Return>", lambda _event: self.start_dashboard())
        self.root.bind("<Control-s>", lambda _event: self.start_dashboard())

        # persistent top toolbar so Start is always visible
        self.toolbar = tk.Frame(self.root, bg=self.theme["panel"], height=54)
        self.toolbar.pack(fill="x", side="top")

        tb_start = tk.Button(
            self.toolbar,
            text="开始展示",
            font=("Arial", 11, "bold"),
            fg=self.theme["text"],
            bg=self.theme["accent"],
            activebackground=self.theme["accent_alt"],
            bd=0,
            padx=12,
            pady=6,
            command=self.start_dashboard,
        )
        tb_start.pack(side="left", padx=8, pady=6)

        tb_settings = tk.Button(
            self.toolbar,
            text="设置",
            font=("Arial", 11),
            fg=self.theme["text"],
            bg=self.theme["panel_alt"],
            activebackground=self.theme["panel"],
            bd=0,
            padx=10,
            pady=6,
            command=self._back_to_setup,
        )
        tb_settings.pack(side="left", padx=6, pady=6)

        tb_quit = tk.Button(
            self.toolbar,
            text="退出",
            font=("Arial", 11),
            fg=self.theme["text"],
            bg="#2b3142",
            activebackground="#3a4154",
            bd=0,
            padx=10,
            pady=6,
            command=self.exit_app,
        )
        tb_quit.pack(side="right", padx=8, pady=6)

        self.canvas = tk.Canvas(self.root, bg=self.theme["bg"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self._create_background()
        self._render_setup_view()
        self._animate_background()
        self._update_clock()

    def _create_background(self) -> None:
        palette = [
            "#10203a",
            "#13243d",
            "#17314a",
            "#1b3954",
            "#203e5c",
            "#0f1d31",
        ]
        for _ in range(12):
            orb = {
                "x": random.randint(0, 1280),
                "y": random.randint(0, 800),
                "dx": random.uniform(-0.35, 0.35),
                "dy": random.uniform(-0.25, 0.25),
                "base_r": random.randint(80, 200),
                "phase": random.uniform(0, math.tau),
                "colors": palette,
            }
            orb["id"] = self.canvas.create_oval(0, 0, 1, 1, fill=palette[0], outline=palette[0])
            self.orbs.append(orb)

    def _create_card(self, width: int, height: int) -> tk.Frame:
        card = tk.Frame(
            self.canvas,
            bg=self.theme["panel"],
            highlightthickness=1,
            highlightbackground=self.theme["line"],
            bd=0,
        )
        card.configure(width=width, height=height)
        card.pack_propagate(False)
        return card

    def _swap_card(self, card: tk.Frame, width: int, height: int) -> None:
        if self.card_window is not None:
            self.canvas.delete(self.card_window)
        if self.card is not None:
            self.card.destroy()
        self.card = card
        self.card_window = self.canvas.create_window(
            self.root.winfo_width() // 2,
            self.root.winfo_height() // 2,
            window=card,
            anchor="center",
            width=width,
            height=height,
        )

    def _clear_card(self) -> None:
        if self.card_window is not None:
            self.canvas.delete(self.card_window)
            self.card_window = None
        if self.card is not None:
            self.card.destroy()
            self.card = None

    def _on_canvas_resize(self, event: tk.Event) -> None:
        if self.card_window is not None:
            self.canvas.coords(self.card_window, event.width // 2, event.height // 2)

    def _render_setup_view(self) -> None:
        self._clear_card()

        card = self._create_card(920, 620)

        header = tk.Frame(card, bg=self.theme["panel"])
        header.pack(fill="x", padx=34, pady=(28, 12))

        title = tk.Label(
            header,
            text="Task Reminder",
            font=("Arial", 30, "bold"),
            fg=self.theme["text"],
            bg=self.theme["panel"],
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="把今天最重要的目标放到屏幕正中，减少拖延，增加提醒频率。",
            font=("Arial", 14),
            fg=self.theme["muted"],
            bg=self.theme["panel"],
        )
        subtitle.pack(anchor="w", pady=(10, 0))

        form = tk.Frame(card, bg=self.theme["panel"])
        form.pack(fill="both", expand=True, padx=34, pady=(10, 20))

        self.task_entry = self._build_input_row(form, "任务名称", "例如：英语单词 / 数学错题 / 项目发布")
        self.deadline_entry = self._build_input_row(form, "截止日期", "例如：05/09/2026 或 05/09/2026 18:30")
        self.note_entry = self._build_input_row(form, "今日提醒", "例如：先做最难的部分，哪怕只有 15 分钟")

        helper = tk.Label(
            form,
            text="提示：如果只输入日期，系统会把截止时间自动设置为当天 23:59:59。",
            font=("Arial", 11),
            fg=self.theme["muted"],
            bg=self.theme["panel"],
        )
        helper.pack(anchor="w", pady=(0, 10))

        preset_row = tk.Frame(form, bg=self.theme["panel"])
        preset_row.pack(fill="x", pady=(4, 14))

        for label, days in (("7 天", 7), ("30 天", 30), ("90 天", 90)):
            button = tk.Button(
                preset_row,
                text=label,
                font=("Arial", 12, "bold"),
                fg=self.theme["text"],
                bg=self.theme["panel_alt"],
                activebackground=self.theme["accent"],
                activeforeground="#0b1220",
                bd=0,
                padx=20,
                pady=10,
                command=lambda value=days: self._set_deadline_days(value),
            )
            button.pack(side="left", padx=(0, 10))

        self.message_var = tk.StringVar(value="")
        self.message_label = tk.Label(
            form,
            textvariable=self.message_var,
            font=("Arial", 12, "bold"),
            fg=self.theme["danger"],
            bg=self.theme["panel"],
        )
        self.message_label.pack(anchor="w", pady=(0, 10))

        action_row = tk.Frame(form, bg=self.theme["panel"])
        action_row.pack(fill="x", pady=(10, 0))

        start_button = tk.Button(
            action_row,
            text="开始展示",
            font=("Arial", 14, "bold"),
            fg="#08101d",
            bg=self.theme["accent"],
            activebackground="#a7dcff",
            activeforeground="#08101d",
            bd=0,
            padx=28,
            pady=14,
            command=self.start_dashboard,
        )
        start_button.pack(side="left")

        demo_button = tk.Button(
            action_row,
            text="填入示例",
            font=("Arial", 12, "bold"),
            fg=self.theme["text"],
            bg=self.theme["panel_alt"],
            activebackground=self.theme["accent_alt"],
            activeforeground="#08101d",
            bd=0,
            padx=22,
            pady=14,
            command=self._fill_example,
        )
        demo_button.pack(side="left", padx=12)

        exit_button = tk.Button(
            action_row,
            text="退出",
            font=("Arial", 12, "bold"),
            fg=self.theme["text"],
            bg="#2b3142",
            activebackground="#3a4154",
            activeforeground=self.theme["text"],
            bd=0,
            padx=22,
            pady=14,
            command=self.exit_app,
        )
        exit_button.pack(side="right")

        footer = tk.Label(
            card,
            text="按 Enter 或 点击 开始展示 启动；F11 切换全屏，Esc 退出。",
            font=("Arial", 11),
            fg=self.theme["muted"],
            bg=self.theme["panel"],
        )
        footer.pack(anchor="w", padx=34, pady=(0, 26))

        self._swap_card(card, 920, 620)

    def _build_input_row(self, parent: tk.Widget, label_text: str, hint_text: str) -> tk.Entry:
        row = tk.Frame(parent, bg=self.theme["panel"])
        row.pack(fill="x", pady=(0, 14))

        label = tk.Label(
            row,
            text=label_text,
            font=("Arial", 13, "bold"),
            fg=self.theme["text"],
            bg=self.theme["panel"],
        )
        label.pack(anchor="w")

        entry = tk.Entry(
            row,
            font=("Arial", 16),
            fg=self.theme["text"],
            bg=self.theme["panel_alt"],
            insertbackground=self.theme["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.theme["line"],
            highlightcolor=self.theme["accent"],
        )
        entry.pack(fill="x", pady=(8, 4), ipady=11)
        entry.insert(0, "")

        hint = tk.Label(
            row,
            text=hint_text,
            font=("Arial", 10),
            fg=self.theme["muted"],
            bg=self.theme["panel"],
        )
        hint.pack(anchor="w")
        return entry

    def _fill_example(self) -> None:
        self.task_entry.delete(0, tk.END)
        self.task_entry.insert(0, "高考冲刺 / 项目完成 / 习惯打卡")
        self.note_entry.delete(0, tk.END)
        self.note_entry.insert(0, "今天至少推进 25 分钟，不要让空想占掉时间。")
        self._set_deadline_days(30)
        self.message_var.set("")

    def load_default_task(self) -> None:
        self.task_entry.delete(0, tk.END)
        self.task_entry.insert(0, "专注学习 / 不要拖延")
        self.deadline_entry.delete(0, tk.END)
        self.deadline_entry.insert(0, (datetime.now() + timedelta(days=30)).strftime("%m/%d/%Y"))
        self.note_entry.delete(0, tk.END)
        self.note_entry.insert(0, "今天先开始 10 分钟，再决定要不要继续。")

    def start_default_countdown(self) -> None:
        self.load_default_task()
        self.start_dashboard()

    def _set_deadline_days(self, days: int) -> None:
        deadline = datetime.now() + timedelta(days=days)
        self.deadline_entry.delete(0, tk.END)
        self.deadline_entry.insert(0, deadline.strftime("%m/%d/%Y"))

    def _parse_deadline(self, raw: str) -> datetime:
        raw = raw.strip()
        if not raw:
            raise ValueError("请先输入截止日期。")

        date_formats = [
            ("%m/%d/%Y %H:%M:%S", False),
            ("%m/%d/%Y %H:%M", False),
            ("%m/%d/%Y", True),
            ("%Y-%m-%d %H:%M:%S", False),
            ("%Y-%m-%d %H:%M", False),
            ("%Y-%m-%d", True),
        ]

        for fmt, end_of_day in date_formats:
            try:
                parsed = datetime.strptime(raw, fmt)
                if end_of_day:
                    return parsed.replace(hour=23, minute=59, second=59)
                return parsed
            except ValueError:
                continue

        raise ValueError("日期格式不正确，请使用 05/09/2026 或 05/09/2026 18:30。")

    def start_dashboard(self) -> None:
        task_name = self.task_entry.get().strip()
        note_text = self.note_entry.get().strip()
        deadline_text = self.deadline_entry.get().strip()

        try:
            deadline = self._parse_deadline(deadline_text)
        except ValueError as exc:
            self.message_var.set(str(exc))
            return

        self.task_name = task_name or "你的目标"
        self.note_text = note_text or "先完成 10 分钟，先行动再优化。"
        self.deadline = deadline
        self.start_time = datetime.now()
        self.last_quote_bucket = None
        self.message_var.set("")

        self.root.title(f"Task Reminder - {self.task_name}")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.is_fullscreen = True
        self._render_dashboard_view()

    def _render_dashboard_view(self) -> None:
        self._clear_card()

        card = self._create_card(1160, 720)
        card.grid_propagate(False)

        top = tk.Frame(card, bg=self.theme["panel"])
        top.pack(fill="x", padx=30, pady=(24, 12))

        self.clock_label = tk.Label(
            top,
            text="",
            font=("Arial", 22, "bold"),
            fg=self.theme["accent"],
            bg=self.theme["panel"],
        )
        self.clock_label.pack(side="left")

        hotkeys = tk.Label(
            top,
            text="F11 全屏 / Esc 退出 / 返回设置",
            font=("Arial", 11),
            fg=self.theme["muted"],
            bg=self.theme["panel"],
        )
        hotkeys.pack(side="right")

        body = tk.Frame(card, bg=self.theme["panel"])
        body.pack(fill="both", expand=True, padx=30, pady=(8, 0))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)

        left = tk.Frame(body, bg=self.theme["panel"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        right = tk.Frame(body, bg=self.theme["panel"])
        right.grid(row=0, column=1, sticky="nsew")

        self.status_badge = tk.Label(
            left,
            text="",
            font=("Arial", 12, "bold"),
            fg="#08101d",
            bg=self.theme["success"],
            padx=12,
            pady=6,
        )
        self.status_badge.pack(anchor="w", pady=(0, 16))

        self.task_label = tk.Label(
            left,
            text=self.task_name,
            font=("Arial", 30, "bold"),
            fg=self.theme["text"],
            bg=self.theme["panel"],
            wraplength=630,
            justify="left",
        )
        self.task_label.pack(anchor="w")

        self.countdown_label = tk.Label(
            left,
            text="",
            font=("Arial", 66, "bold"),
            fg=self.theme["accent"],
            bg=self.theme["panel"],
            pady=16,
        )
        self.countdown_label.pack(anchor="w")

        self.deadline_label = tk.Label(
            left,
            text="",
            font=("Arial", 15),
            fg=self.theme["muted"],
            bg=self.theme["panel"],
        )
        self.deadline_label.pack(anchor="w", pady=(0, 20))

        progress_title = tk.Label(
            left,
            text="进度条",
            font=("Arial", 13, "bold"),
            fg=self.theme["text"],
            bg=self.theme["panel"],
        )
        progress_title.pack(anchor="w", pady=(0, 10))

        self.progress_canvas = tk.Canvas(
            left,
            height=26,
            bg=self.theme["panel"],
            highlightthickness=0,
        )
        self.progress_canvas.pack(fill="x")
        self.progress_bg = self.progress_canvas.create_rectangle(0, 3, 640, 23, fill=self.theme["line"], outline=self.theme["line"])
        self.progress_fill = self.progress_canvas.create_rectangle(0, 3, 0, 23, fill=self.theme["accent"], outline=self.theme["accent"])
        self.progress_text = tk.Label(
            left,
            text="",
            font=("Arial", 12),
            fg=self.theme["muted"],
            bg=self.theme["panel"],
        )
        self.progress_text.pack(anchor="w", pady=(10, 22))

        self.focus_label = tk.Label(
            left,
            text=self.note_text,
            font=("Arial", 16),
            fg=self.theme["text"],
            bg=self.theme["panel_alt"],
            wraplength=620,
            justify="left",
            padx=18,
            pady=18,
            bd=0,
            relief="flat",
        )
        self.focus_label.pack(fill="x", pady=(0, 16))

        button_row = tk.Frame(left, bg=self.theme["panel"])
        button_row.pack(anchor="w", pady=(4, 0))

        back_button = tk.Button(
            button_row,
            text="返回设置",
            font=("Arial", 12, "bold"),
            fg=self.theme["text"],
            bg=self.theme["panel_alt"],
            activebackground=self.theme["accent_alt"],
            activeforeground="#08101d",
            bd=0,
            padx=20,
            pady=12,
            command=self._back_to_setup,
        )
        back_button.pack(side="left", padx=(0, 10))

        quit_button = tk.Button(
            button_row,
            text="退出程序",
            font=("Arial", 12, "bold"),
            fg=self.theme["text"],
            bg="#2b3142",
            activebackground="#3a4154",
            activeforeground=self.theme["text"],
            bd=0,
            padx=20,
            pady=12,
            command=self.exit_app,
        )
        quit_button.pack(side="left")

        quote_frame = tk.Frame(right, bg=self.theme["panel_alt"], padx=20, pady=20)
        quote_frame.pack(fill="x", pady=(0, 18))

        quote_title = tk.Label(
            quote_frame,
            text="今日提醒",
            font=("Arial", 13, "bold"),
            fg=self.theme["accent_alt"],
            bg=self.theme["panel_alt"],
        )
        quote_title.pack(anchor="w")

        self.quote_label = tk.Label(
            quote_frame,
            text="",
            font=("Arial", 17, "bold"),
            fg=self.theme["text"],
            bg=self.theme["panel_alt"],
            wraplength=360,
            justify="left",
            pady=12,
        )
        self.quote_label.pack(anchor="w")

        tiles = tk.Frame(right, bg=self.theme["panel"])
        tiles.pack(fill="both", expand=True)
        tiles.rowconfigure(0, weight=1)
        tiles.rowconfigure(1, weight=1)
        tiles.columnconfigure(0, weight=1)

        self.stats_tile = self._make_tile(
            tiles,
            row=0,
            title="坚持时间",
            body="",
            accent=self.theme["success"],
        )
        self.stats_tile.grid(row=0, column=0, sticky="nsew", pady=(0, 14))

        self.second_tile = self._make_tile(
            tiles,
            row=1,
            title="接下来怎么做",
            body="",
            accent=self.theme["warning"],
        )
        self.second_tile.grid(row=1, column=0, sticky="nsew")

        self._swap_card(card, 1160, 720)

    def _make_tile(self, parent: tk.Widget, row: int, title: str, body: str, accent: str) -> tk.Frame:
        tile = tk.Frame(parent, bg=self.theme["panel_alt"], padx=18, pady=18)
        tile.rowconfigure(1, weight=1)
        tile.columnconfigure(0, weight=1)

        title_label = tk.Label(
            tile,
            text=title,
            font=("Arial", 13, "bold"),
            fg=accent,
            bg=self.theme["panel_alt"],
        )
        title_label.grid(row=0, column=0, sticky="w")

        body_label = tk.Label(
            tile,
            text=body,
            font=("Arial", 16),
            fg=self.theme["text"],
            bg=self.theme["panel_alt"],
            wraplength=330,
            justify="left",
            pady=10,
        )
        body_label.grid(row=1, column=0, sticky="nw")

        tile.title_label = title_label
        tile.body_label = body_label
        return tile

    def _back_to_setup(self) -> None:
        self.root.attributes("-fullscreen", False)
        self.root.attributes("-topmost", False)
        self.is_fullscreen = False
        self.root.title("Task Reminder")
        self._render_setup_view()

    def _remaining_status(self, remaining: timedelta) -> tuple[str, str, str, str]:
        total_seconds = max(int(remaining.total_seconds()), 0)
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if total_seconds <= 0:
            return (
                "已截止",
                "现在就开始",
                "任务已经到期，先做最关键的一步，不要把今天拖成明天。",
                self.theme["danger"],
            )

        if days <= 3:
            badge = "紧急"
            advice = "时间很近了，把注意力收回到最重要的一步。"
            color = self.theme["danger"]
        elif days <= 14:
            badge = "冲刺"
            advice = "保持稳定节奏，少一点犹豫，多一点执行。"
            color = self.theme["warning"]
        else:
            badge = "进行中"
            advice = "节奏拉稳，持续前进，别被拖延偷走积累。"
            color = self.theme["success"]

        countdown = f"{days} 天 {hours:02d}:{minutes:02d}:{seconds:02d}"
        return badge, countdown, advice + f"  当前还剩 {countdown}。", color

    def _update_clock(self) -> None:
        now = datetime.now()
        if hasattr(self, "clock_label"):
            self.clock_label.config(text=now.strftime("%Y-%m-%d  %A  %H:%M:%S"))

        if hasattr(self, "countdown_label"):
            remaining = self.deadline - now
            badge, countdown, advice, color = self._remaining_status(remaining)
            self.status_badge.config(text=badge, bg=color)
            self.countdown_label.config(text=countdown)
            self.deadline_label.config(text=f"截止日期：{self.deadline.strftime('%Y-%m-%d %H:%M:%S')}")

            total_span = max((self.deadline - self.start_time).total_seconds(), 1)
            progress = (now - self.start_time).total_seconds() / total_span
            progress = max(0.0, min(progress, 1.0))
            bar_width = 640
            fill_width = int(bar_width * progress)
            self.progress_canvas.coords(self.progress_fill, 0, 3, fill_width, 23)
            self.progress_text.config(text=f"已完成 {progress * 100:.0f}%  |  {advice}")

            elapsed_days = max((now - self.start_time).days, 0)
            self.stats_tile.body_label.config(
                text=f"已经坚持 {elapsed_days} 天。\n把今天的第一步完成，再考虑后面的步骤。"
            )

            self.second_tile.body_label.config(
                text=self.note_text if self.note_text else "今天先做 10 分钟，先打开局面。"
            )

            bucket = int(now.timestamp() // 12)
            if self.last_quote_bucket != bucket:
                self.last_quote_bucket = bucket
                quote = self.quotes[bucket % len(self.quotes)]
                if hasattr(self, "quote_label"):
                    self.quote_label.config(text=quote)

        self.root.after(1000, self._update_clock)

    def _animate_background(self) -> None:
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        phase = datetime.now().timestamp() / 4.0

        for index, orb in enumerate(self.orbs):
            orb["x"] += orb["dx"]
            orb["y"] += orb["dy"]

            if orb["x"] < -260:
                orb["x"] = width + 260
            elif orb["x"] > width + 260:
                orb["x"] = -260

            if orb["y"] < -260:
                orb["y"] = height + 260
            elif orb["y"] > height + 260:
                orb["y"] = -260

            pulse = 0.88 + 0.12 * math.sin(phase + orb["phase"])
            radius = orb["base_r"] * pulse
            shade_index = int((phase + orb["phase"] + index) * 1.5) % len(orb["colors"])
            color = orb["colors"][shade_index]
            self.canvas.coords(orb["id"], orb["x"] - radius, orb["y"] - radius, orb["x"] + radius, orb["y"] + radius)
            self.canvas.itemconfig(orb["id"], fill=color, outline=color)

        self.root.after(40, self._animate_background)

    def toggle_fullscreen(self) -> None:
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        if self.is_fullscreen:
            self.root.attributes("-topmost", True)

    def exit_app(self) -> None:
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    TaskReminderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

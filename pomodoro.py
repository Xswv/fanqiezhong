"""
番茄钟计时器 - Pomodoro Timer
使用 Python + Tkinter 构建的桌面番茄时钟软件
功能：自定义时长、系统通知、简洁现代的界面
"""

import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime

# 尝试导入 winsound（Windows 系统声音）
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

# 尝试加载 plyer 用于跨平台通知
try:
    from plyer import notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False


class PomodoroTimer:
    """番茄钟计时器主类"""

    # 默认时间设置（分钟）
    DEFAULT_WORK_TIME = 25
    DEFAULT_SHORT_BREAK = 5
    DEFAULT_LONG_BREAK = 15
    POMODORO_UNTIL_LONG_BREAK = 4  # 几个番茄后长休息

    # 颜色配置 - 简洁现代风格
    COLORS = {
        'work': '#E74C3C',      # 红色 - 工作时间
        'short_break': '#27AE60',  # 绿色 - 短休息
        'long_break': '#3498DB',   # 蓝色 - 长休息
        'bg': '#1E1E2E',        # 深蓝灰背景
        'bg_secondary': '#2D2D44',  # 次级背景
        'text': '#FFFFFF',      # 主文本
        'text_secondary': '#A0A0B0',  # 次级文本
        'accent': '#FF6B6B',    # 强调色
        'button': '#4A4A6A',    # 按钮颜色
        'button_hover': '#5A5A7A',  # 按钮悬停
    }

    def __init__(self):
        """初始化番茄钟"""
        self.root = tk.Tk()
        self.root.title("番茄钟")
        self.root.geometry("420x580")
        self.root.resizable(False, False)
        self.root.configure(bg=self.COLORS['bg'])

        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap(default='tomato.ico')
        except:
            pass

        # 时间设置（秒）
        self.work_time = self.DEFAULT_WORK_TIME * 60
        self.short_break = self.DEFAULT_SHORT_BREAK * 60
        self.long_break = self.DEFAULT_LONG_BREAK * 60

        # 计时器状态
        self.current_mode = 'work'  # work, short_break, long_break
        self.remaining_time = self.work_time
        self.is_running = False
        self.timer_id = None
        self.pomodoro_count = 0  # 完成的番茄数

        # 加载保存的设置
        self.load_settings()

        # 创建界面
        self.setup_ui()

        # 绑定快捷键
        self.root.bind('<space>', lambda e: self.toggle_timer())
        self.root.bind('<r>', lambda e: self.reset_timer())
        self.root.bind('<Escape>', lambda e: self.show_settings())

        # 窗口关闭处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """设置用户界面"""
        # 主容器
        self.main_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 模式标签
        self.mode_label = tk.Label(
            self.main_frame,
            text="工作时间",
            font=('Microsoft YaHei', 18, 'bold'),
            fg=self.COLORS['text_secondary'],
            bg=self.COLORS['bg']
        )
        self.mode_label.pack(pady=(10, 5))

        # 圆形进度条画布
        self.canvas_size = 240
        self.canvas = tk.Canvas(
            self.main_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=self.COLORS['bg'],
            highlightthickness=0
        )
        self.canvas.pack(pady=10)

        # 绘制进度圆环
        self.draw_progress_circle()

        # 时间显示（覆盖在圆环上）
        self.time_var = tk.StringVar(value=self.format_time(self.remaining_time))
        self.time_label = tk.Label(
            self.main_frame,
            textvariable=self.time_var,
            font=('Consolas', 48, 'bold'),
            fg=self.COLORS['text'],
            bg=self.COLORS['bg']
        )
        self.time_label.place(relx=0.5, rely=0.42, anchor='center')

        # 番茄计数
        self.count_label = tk.Label(
            self.main_frame,
            text=f"🍅 今日完成: {self.pomodoro_count}",
            font=('Microsoft YaHei', 12),
            fg=self.COLORS['text_secondary'],
            bg=self.COLORS['bg']
        )
        self.count_label.pack(pady=5)

        # 控制按钮框架
        button_frame = tk.Frame(self.main_frame, bg=self.COLORS['bg'])
        button_frame.pack(pady=20)

        # 开始/暂停按钮
        self.start_button = tk.Button(
            button_frame,
            text="▶ 开始",
            font=('Microsoft YaHei', 14, 'bold'),
            fg=self.COLORS['text'],
            bg=self.COLORS['button'],
            activebackground=self.COLORS['button_hover'],
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor='hand2',
            command=self.toggle_timer
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        # 重置按钮
        self.reset_button = tk.Button(
            button_frame,
            text="↺ 重置",
            font=('Microsoft YaHei', 12),
            fg=self.COLORS['text'],
            bg=self.COLORS['button'],
            activebackground=self.COLORS['button_hover'],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.reset_timer
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # 设置按钮
        self.settings_button = tk.Button(
            button_frame,
            text="⚙",
            font=('Microsoft YaHei', 12),
            fg=self.COLORS['text'],
            bg=self.COLORS['button'],
            activebackground=self.COLORS['button_hover'],
            relief=tk.FLAT,
            padx=15,
            pady=10,
            cursor='hand2',
            command=self.show_settings
        )
        self.settings_button.pack(side=tk.LEFT, padx=5)

        # 模式切换按钮
        mode_frame = tk.Frame(self.main_frame, bg=self.COLORS['bg'])
        mode_frame.pack(pady=10)

        modes = [
            ('工作', 'work', self.COLORS['work']),
            ('短休息', 'short_break', self.COLORS['short_break']),
            ('长休息', 'long_break', self.COLORS['long_break']),
        ]

        for text, mode, color in modes:
            btn = tk.Button(
                mode_frame,
                text=text,
                font=('Microsoft YaHei', 10),
                fg=color,
                bg=self.COLORS['bg_secondary'],
                activebackground=self.COLORS['button_hover'],
                relief=tk.FLAT,
                padx=15,
                pady=5,
                cursor='hand2',
                command=lambda m=mode: self.switch_mode(m)
            )
            btn.pack(side=tk.LEFT, padx=3)

        # 快捷键提示
        hint_label = tk.Label(
            self.main_frame,
            text="空格: 开始/暂停 | R: 重置 | Esc: 设置",
            font=('Microsoft YaHei', 9),
            fg=self.COLORS['text_secondary'],
            bg=self.COLORS['bg']
        )
        hint_label.pack(side=tk.BOTTOM, pady=10)

    def draw_progress_circle(self):
        """绘制圆形进度条"""
        self.canvas.delete("all")

        center_x = self.canvas_size // 2
        center_y = self.canvas_size // 2
        radius = 100
        line_width = 12

        # 获取当前模式的颜色
        color = self.COLORS.get(self.current_mode, self.COLORS['work'])

        # 绘制背景圆环
        self.canvas.create_arc(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            start=90, extent=360,
            style='arc', outline=self.COLORS['bg_secondary'],
            width=line_width
        )

        # 计算进度
        total_time = self.get_current_mode_time()
        if total_time > 0:
            progress = (total_time - self.remaining_time) / total_time
        else:
            progress = 0

        # 绘制进度圆环
        if progress > 0:
            extent = -progress * 360  # 负值表示顺时针
            self.canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=90, extent=extent,
                style='arc', outline=color,
                width=line_width
            )

        # 绘制番茄图标（简单圆形表示）
        tomato_radius = 15
        self.canvas.create_oval(
            center_x - tomato_radius, center_y - tomato_radius - 50,
            center_x + tomato_radius, center_y + tomato_radius - 50,
            fill=self.COLORS['work'] if self.current_mode == 'work' else color,
            outline=''
        )

    def get_current_mode_time(self):
        """获取当前模式的总时间"""
        if self.current_mode == 'work':
            return self.work_time
        elif self.current_mode == 'short_break':
            return self.short_break
        else:
            return self.long_break

    def format_time(self, seconds):
        """格式化时间显示"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def toggle_timer(self):
        """切换计时器状态（开始/暂停）"""
        if self.is_running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        """开始计时"""
        self.is_running = True
        self.start_button.configure(text="⏸ 暂停")
        self.update_timer()

    def pause_timer(self):
        """暂停计时"""
        self.is_running = False
        self.start_button.configure(text="▶ 继续")
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def reset_timer(self):
        """重置计时器"""
        self.pause_timer()
        self.remaining_time = self.get_current_mode_time()
        self.time_var.set(self.format_time(self.remaining_time))
        self.draw_progress_circle()
        self.start_button.configure(text="▶ 开始")

    def update_timer(self):
        """更新计时器"""
        if not self.is_running:
            return

        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.time_var.set(self.format_time(self.remaining_time))
            self.draw_progress_circle()
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            # 计时结束
            self.timer_finished()

    def timer_finished(self):
        """计时结束处理"""
        self.is_running = False
        self.play_sound()
        self.show_notification()

        if self.current_mode == 'work':
            self.pomodoro_count += 1
            self.count_label.configure(text=f"🍅 今日完成: {self.pomodoro_count}")

            # 判断是否该长休息
            if self.pomodoro_count % self.POMODORO_UNTIL_LONG_BREAK == 0:
                self.switch_mode('long_break')
            else:
                self.switch_mode('short_break')
        else:
            # 休息结束，回到工作
            self.switch_mode('work')

        self.start_button.configure(text="▶ 开始")
        self.save_settings()

    def switch_mode(self, mode):
        """切换模式"""
        self.pause_timer()
        self.current_mode = mode

        if mode == 'work':
            self.remaining_time = self.work_time
            self.mode_label.configure(text="工作时间", fg=self.COLORS['work'])
        elif mode == 'short_break':
            self.remaining_time = self.short_break
            self.mode_label.configure(text="短休息", fg=self.COLORS['short_break'])
        else:
            self.remaining_time = self.long_break
            self.mode_label.configure(text="长休息", fg=self.COLORS['long_break'])

        self.time_var.set(self.format_time(self.remaining_time))
        self.draw_progress_circle()
        self.start_button.configure(text="▶ 开始")

    def play_sound(self):
        """播放提示音"""
        if HAS_WINSOUND:
            # Windows 系统声音
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            # 尝试使用系统 bell
            self.root.bell()

    def show_notification(self):
        """显示系统通知"""
        title = "番茄钟"
        if self.current_mode == 'work':
            message = "工作时间结束！该休息了 🎉"
        else:
            message = "休息结束！开始新的番茄吧 💪"

        if HAS_PLYER:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    timeout=5
                )
            except:
                pass
        else:
            # 使用 Tkinter 的 messagebox 作为备选
            self.root.after(100, lambda: messagebox.showinfo(title, message))

    def show_settings(self):
        """显示设置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("350x400")
        settings_window.resizable(False, False)
        settings_window.configure(bg=self.COLORS['bg'])
        settings_window.transient(self.root)
        settings_window.grab_set()

        # 设置标题
        tk.Label(
            settings_window,
            text="⚙ 设置",
            font=('Microsoft YaHei', 18, 'bold'),
            fg=self.COLORS['text'],
            bg=self.COLORS['bg']
        ).pack(pady=20)

        # 时间设置
        time_settings = [
            ("工作时间 (分钟):", self.work_time // 60, 'work'),
            ("短休息 (分钟):", self.short_break // 60, 'short_break'),
            ("长休息 (分钟):", self.long_break // 60, 'long_break'),
        ]

        entries = {}
        for label_text, default_value, key in time_settings:
            frame = tk.Frame(settings_window, bg=self.COLORS['bg'])
            frame.pack(fill=tk.X, padx=30, pady=10)

            tk.Label(
                frame,
                text=label_text,
                font=('Microsoft YaHei', 12),
                fg=self.COLORS['text'],
                bg=self.COLORS['bg']
            ).pack(side=tk.LEFT)

            entry = tk.Entry(
                frame,
                font=('Consolas', 12),
                width=8,
                justify='center'
            )
            entry.insert(0, str(default_value))
            entry.pack(side=tk.RIGHT)
            entries[key] = entry

        # 保存按钮
        def save():
            try:
                self.work_time = int(entries['work'].get()) * 60
                self.short_break = int(entries['short_break'].get()) * 60
                self.long_break = int(entries['long_break'].get()) * 60

                # 验证输入
                if any(t <= 0 for t in [self.work_time, self.short_break, self.long_break]):
                    raise ValueError("时间必须大于0")

                self.reset_timer()
                self.save_settings()
                settings_window.destroy()
            except ValueError as e:
                messagebox.showerror("错误", f"请输入有效的数字！\n{str(e)}")

        tk.Button(
            settings_window,
            text="保存",
            font=('Microsoft YaHei', 12, 'bold'),
            fg=self.COLORS['text'],
            bg=self.COLORS['button'],
            activebackground=self.COLORS['button_hover'],
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor='hand2',
            command=save
        ).pack(pady=20)

        # 重置为默认值
        def reset_defaults():
            for key, (_, default, _) in zip(entries.keys(), time_settings):
                entries[key].delete(0, tk.END)
                entries[key].insert(0, str(default))

        tk.Button(
            settings_window,
            text="恢复默认",
            font=('Microsoft YaHei', 10),
            fg=self.COLORS['text_secondary'],
            bg=self.COLORS['bg'],
            relief=tk.FLAT,
            cursor='hand2',
            command=reset_defaults
        ).pack()

    def save_settings(self):
        """保存设置到文件"""
        settings = {
            'work_time': self.work_time,
            'short_break': self.short_break,
            'long_break': self.long_break,
            'pomodoro_count': self.pomodoro_count,
            'last_date': datetime.now().strftime('%Y-%m-%d')
        }

        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except:
            pass

    def load_settings(self):
        """从文件加载设置"""
        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                # 如果是新的一天，重置计数
                if settings.get('last_date') != datetime.now().strftime('%Y-%m-%d'):
                    self.pomodoro_count = 0
                else:
                    self.pomodoro_count = settings.get('pomodoro_count', 0)

                self.work_time = settings.get('work_time', self.work_time)
                self.short_break = settings.get('short_break', self.short_break)
                self.long_break = settings.get('long_break', self.long_break)
        except:
            pass

    def on_closing(self):
        """窗口关闭处理"""
        self.pause_timer()
        self.save_settings()
        self.root.destroy()

    def run(self):
        """运行应用"""
        self.root.mainloop()


def main():
    """主函数"""
    app = PomodoroTimer()
    app.run()


if __name__ == '__main__':
    main()

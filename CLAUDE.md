# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

番茄钟计时器 - 一个简洁现代的桌面番茄时钟软件，使用 Python + Tkinter 构建。

## Running the Application

```bash
# 直接运行
python pomodoro.py

# 或双击 run.bat
```

可选依赖（用于系统通知）：
```bash
pip install plyer
```

## Architecture

单文件应用，所有代码在 `pomodoro.py` 中。

### 核心类：`PomodoroTimer`

- **`__init__`** - 初始化窗口、加载设置、创建界面、绑定快捷键
- **`setup_ui`** - 创建所有界面元素（模式标签、圆形进度条、时间显示、按钮）
- **`draw_progress_circle`** - 绘制圆形进度条和番茄图标
- **`update_timer`** - 计时器主循环，每秒更新显示
- **`timer_finished`** - 计时结束处理（通知、声音、模式切换）
- **`switch_mode`** - 切换工作/短休息/长休息模式
- **`show_settings`** - 创建设置窗口
- **`save_settings` / `load_settings`** - 持久化用户设置到 `settings.json`

### 状态管理

- 工作时长、休息时长存储在实例变量中（秒）
- 设置自动保存到 `settings.json`（位于脚本同目录）
- 番茄计数按天重置

### 颜色主题

修改 `COLORS` 字典自定义界面颜色。

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `空格` | 开始/暂停计时 |
| `R` | 重置计时器 |
| `Esc` | 打开设置 |

## 界面模式

- **红色** - 工作时间（默认25分钟）
- **绿色** - 短休息（默认5分钟）
- **蓝色** - 长休息（默认15分钟，每4个番茄后）

import json
import os
import re
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, scrolledtext, TclError

import tkinter as tk
import tkinter.font as tkfont

class CustomToast:
    def __init__(self, parent):
        self.parent = parent

    def show(self, title, message, duration=3000, bootstyle="success"):
        # 创建顶层窗口
        toast_window = tk.Toplevel(self.parent)
        toast_window.overrideredirect(True)  # 无边框
        toast_window.attributes('-topmost', True)  # 置顶

        # 更新样式颜色为更柔和、专业的配色
        bg_colors = {
            "success": "#e6f3e6",  # 更浅的绿色
            "warning": "#fff3cd",  # 更浅的黄色
            "danger": "#f8d7da",   # 更浅的红色
            "info": "#d1ecf1"      # 更浅的蓝色
        }
        title_colors = {
            "success": "#155724",  # 深绿色
            "warning": "#856404",  # 深黄色
            "danger": "#721c24",   # 深红色
            "info": "#0c5460"      # 深蓝色
        }
        message_colors = {
            "success": "#2a6817",  # 稍浅的绿色
            "warning": "#9c7d14",  # 稍浅的黄色
            "danger": "#a12a33",   # 稍浅的红色
            "info": "#1a7a8f"      # 稍浅的蓝色
        }

        bg_color = bg_colors.get(bootstyle, "#e6f3e6")
        title_color = title_colors.get(bootstyle, "#155724")
        message_color = message_colors.get(bootstyle, "#2a6817")

        # 配置窗口样式
        toast_window.configure(bg=bg_color)

        # 创建标签
        title_label = tk.Label(toast_window, text=title,
                                font=('Microsoft YaHei', 12, 'bold'),
                                bg=bg_color, fg=title_color)
        message_label = tk.Label(toast_window, text=message,
                                 font=('Microsoft YaHei', 10),
                                 bg=bg_color, fg=message_color,
                                 wraplength=250)

        # 布局
        title_label.pack(padx=10, pady=(10, 5), anchor='w')
        message_label.pack(padx=10, pady=(0, 10), anchor='w')

        # 计算位置（GUI右下角）
        window_width = self.parent.winfo_width()
        window_height = self.parent.winfo_height()
        toast_width = 300
        toast_height = 100

        # 获取父窗口在屏幕上的位置
        x = self.parent.winfo_rootx() + window_width - toast_width - 20
        y = self.parent.winfo_rooty() + window_height - toast_height - 20

        # 设置窗口位置和大小
        toast_window.geometry(f'{toast_width}x{toast_height}+{x}+{y}')

        # 添加淡出效果
        toast_window.attributes('-alpha', 1.0)

        def fade_out():
            current_alpha = toast_window.attributes('-alpha')
            if current_alpha > 0:
                toast_window.attributes('-alpha', current_alpha - 0.1)
                toast_window.after(50, fade_out)
            else:
                toast_window.destroy()

        # 定时关闭
        toast_window.after(duration, fade_out)


class FileRenamerApp:
    CONFIG_FILE = os.path.join(
        os.path.expanduser('~'),
        '.config',
        'episode_renamer',
        'config.json'
    )

    def __init__(self, master):
        # 确保配置文件目录存在
        os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)

        self.master = master
        self.toast = CustomToast(master)
        master.title("媒体文件重命名助手")

        # 获取屏幕宽度和高度
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        # 设置窗口大小为屏幕的60%
        window_width = int(screen_width * 0.6)
        window_height = int(screen_height * 0.92)

        # x坐标设置为屏幕右侧1/2处
        x = int(screen_width * 0.4)

        # y坐标设置为0
        y = 0

        # 设置窗口大小和位置
        master.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 主容器
        self.main_container = ttk.Frame(master, padding="15 10 15 10")
        self.main_container.pack(fill=BOTH, expand=YES)

        # 创建样式
        style = ttk.Style()
        # 增大字体并加粗
        style.configure('TLabel', font=('Microsoft YaHei', 11))
        style.configure('TEntry', font=('Microsoft YaHei', 11))
        style.configure('TButton', font=('Microsoft YaHei', 11, 'bold'))
        style.configure('TLabelframe.Label', font=('Microsoft YaHei', 13, 'bold'))

        # 标题
        self.title_label = ttk.Label(
            self.main_container,
            text="媒体文件重命名助手",
            font=('Microsoft YaHei', 16, 'bold'),
            bootstyle=PRIMARY
        )
        self.title_label.pack(pady=(0, 10))

        # 目录选择
        dir_frame = ttk.Frame(self.main_container)
        dir_frame.pack(fill=X, pady=5)

        self.dir_label = ttk.Label(dir_frame, text="当前目录：", bootstyle=SECONDARY)
        self.dir_label.pack(side=LEFT, padx=10)

        self.select_dir_button = ttk.Button(
            dir_frame,
            text="选择文件夹",
            command=self.select_directory,
            bootstyle=PRIMARY,
            width=12
        )
        self.select_dir_button.pack(side=RIGHT, padx=10)

        # 加载上次选择的目录
        self.current_dir = self.load_last_directory()
        os.chdir(self.current_dir)
        self.dir_label.config(text=f"当前目录：{self.current_dir}")

        # 季号集号调整区域
        season_episode_frame = ttk.LabelFrame(
            self.main_container,
            text="季号集号调整",
            bootstyle=INFO,
            padding=10
        )
        season_episode_frame.pack(fill=X, pady=5)

        # 创建一个网格布局的容器用于原文件和新文件信息
        info_container = ttk.Frame(season_episode_frame)
        info_container.pack(fill=X, pady=5)

        # 原文件信息区域
        old_info_frame = ttk.LabelFrame(
            info_container,
            text="原文件信息",
            bootstyle=PRIMARY,
            padding=10
        )
        old_info_frame.pack(side=LEFT, padx=(0, 5), fill=X, expand=YES)

        # 原文件季号
        ttk.Label(old_info_frame, text="季号:").grid(row=0, column=0, padx=(0, 5), pady=5, sticky=W)
        self.old_season_entry = ttk.Entry(old_info_frame, width=10)
        self.old_season_entry.grid(row=0, column=1, padx=(0, 10), pady=5)

        # 原文件集号
        ttk.Label(old_info_frame, text="集号起始:").grid(row=1, column=0, padx=(0, 5), pady=5, sticky=W)
        self.old_episode_start = ttk.Entry(old_info_frame, width=10)
        self.old_episode_start.grid(row=1, column=1, padx=(0, 10), pady=5)

        ttk.Label(old_info_frame, text="集号截止:[不填默认999]").grid(row=1, column=2, padx=(0, 5), pady=5, sticky=W)
        self.old_episode_end = ttk.Entry(old_info_frame, width=10)
        self.old_episode_end.grid(row=1, column=3, padx=(0, 10), pady=5)

        # 新文件信息区域
        new_info_frame = ttk.LabelFrame(
            info_container,
            text="新文件信息",
            bootstyle=SUCCESS,
            padding=10
        )
        new_info_frame.pack(side=RIGHT, padx=(5, 0), fill=X, expand=YES)

        # 新文件季号
        ttk.Label(new_info_frame, text="季号:").grid(row=0, column=0, padx=(0, 5), pady=5, sticky=W)
        self.new_season_entry = ttk.Entry(new_info_frame, width=10)
        self.new_season_entry.grid(row=0, column=1, padx=(0, 10), pady=5)

        # 新文件集号
        ttk.Label(new_info_frame, text="集号起始:").grid(row=1, column=0, padx=(0, 5), pady=5, sticky=W)
        self.new_episode_start = ttk.Entry(new_info_frame, width=10)
        self.new_episode_start.grid(row=1, column=1, padx=(0, 10), pady=5)

        ttk.Label(new_info_frame, text="集号截止:[不填自动跟随]").grid(row=1, column=2, padx=(0, 5), pady=5, sticky=W)
        self.new_episode_end = ttk.Entry(new_info_frame, width=10)
        self.new_episode_end.grid(row=1, column=3, padx=(0, 10), pady=5)

        # 操作按钮
        btn_frame = ttk.Frame(season_episode_frame)
        btn_frame.pack(fill=X, pady=5)

        self.preview_button = ttk.Button(
            btn_frame,
            text="预览重命名",
            command=self.preview_rename,
            bootstyle=SUCCESS,
            width=15
        )
        self.preview_button.pack(side=LEFT, expand=YES, padx=10)

        self.rename_button = ttk.Button(
            btn_frame,
            text="执行重命名",
            command=self.rename_files,
            bootstyle=DANGER,
            state=DISABLED,
            width=15
        )
        self.rename_button.pack(side=LEFT, expand=YES, padx=10)

        # 预览区域
        self.preview_frame = ttk.LabelFrame(
            self.main_container,
            text="预览区",
            bootstyle=INFO,
            padding=10
        )

        self.preview_text = scrolledtext.ScrolledText(
            self.preview_frame,
            height=15,  # 增大高度
            width=70,
            font=('Consolas', 11)  # 稍微调小字体
        )
        self.preview_text.pack(padx=10, pady=10, fill=BOTH, expand=YES)

        # 绑定事件
        self.old_episode_start.bind('<FocusOut>', self.auto_calculate_end)
        self.old_episode_end.bind('<FocusOut>', self.auto_calculate_end)
        self.new_episode_start.bind('<FocusOut>', self.auto_calculate_end)

        # 当前工作目录
        self.current_dir = os.getcwd()
        self.dir_label.config(text=f"当前目录：{self.current_dir}")

        # 存储重命名列表
        self.rename_list = []

    def auto_calculate_end(self, event=None):
        """
        自动计算集号截止和新集号范围
        """
        try:
            # 获取原文件集号的起始
            old_start = int(self.old_episode_start.get())

            # 获取原文件集号的截止，未输入时默认为999
            try:
                old_end = int(self.old_episode_end.get())
            except (ValueError, TclError):
                old_end = 999
                self.old_episode_end.delete(0, END)
                self.old_episode_end.insert(0, str(old_end))

            # 获取新文件集号的起始
            new_start = int(self.new_episode_start.get())

            # 计算原文件集号的范围
            old_range = old_end - old_start + 1

            # 自动计算新文件集号的截止
            new_end = new_start + old_range - 1

            # 设置新文件集号的截止
            self.new_episode_end.delete(0, END)
            self.new_episode_end.insert(0, str(new_end))
        except (ValueError, TclError):
            # 如果输入无效，不做任何处理
            pass

    def load_last_directory(self):
        """
        加载上次选择的目录
        """
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    last_dir = config.get('last_directory', os.getcwd())
                    # 检查目录是否存在且可访问
                    if os.path.isdir(last_dir) and os.access(last_dir, os.R_OK):
                        return last_dir
        except (json.JSONDecodeError, PermissionError):
            pass

        # 如果无法读取或目录不可用，返回当前工作目录
        return os.getcwd()
    def save_last_directory(self, directory):
        """
        保存最后选择的目录
        """
        try:
            config = {'last_directory': directory}
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"无法保存目录配置：{e}")
    def select_directory(self):
        """
        选择文件夹
        """
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            self.current_dir = selected_dir
            self.dir_label.config(text=f"当前目录：{self.current_dir}")
            os.chdir(self.current_dir)

            # 保存最后选择的目录
            self.save_last_directory(self.current_dir)

    def preview_rename(self):
        """预览重命名文件"""
        try:
            # 重置预览和重命名按钮状态
            self.preview_text.delete('1.0', END)
            self.rename_button.config(state=DISABLED)
            self.rename_list = []

            # 获取输入值
            old_season = int(self.old_season_entry.get())
            old_episode_start = int(self.old_episode_start.get())

            # 原集号截止默认为999
            try:
                old_episode_end = int(self.old_episode_end.get())
            except (ValueError, TclError):
                old_episode_end = 999
                self.old_episode_end.delete(0, END)
                self.old_episode_end.insert(0, str(old_episode_end))

            new_season = int(self.new_season_entry.get())
            new_episode_start = int(self.new_episode_start.get())

            # 新集号截止自动计算
            new_episode_end = new_episode_start + (old_episode_end - old_episode_start)

            self.new_episode_end.delete(0, END)
            self.new_episode_end.insert(0, str(new_episode_end))

            # 检查是否实际需要重命名
            if (old_season == new_season and
                    old_episode_start == new_episode_start and
                    old_episode_end == new_episode_end):
                self.toast.show(
                    title="提示",
                    message="原文件信息与新文件信息相同，无需重命名",
                    duration=3000,
                    bootstyle="warning"
                )
                return

            # 处理扩展名
            extension = self.extension_entry.get().strip()
            # 默认设置extension_pattern
            extension_pattern = '*'

            if extension == '*':
                # 如果是*，则查找所有文件
                extension_pattern = '*'
            else:
                # 确保扩展名以点开头
                extension = extension if extension.startswith('.') else '.' + extension
                # 设置具体的扩展名匹配
                extension_pattern = extension

            # 预览重命名
            rename_list = []

            # 计算需要重命名的文件数量
            rename_count = old_episode_end - old_episode_start + 1

            for i in range(rename_count):
                old_episode = old_episode_start + i
                new_episode = new_episode_start + i

                # 使用正则表达式匹配文件
                pattern = re.compile(rf'(.*?)S{old_season:02d}E{old_episode:02d}(.*)')

                # 根据扩展名查找文件
                if extension_pattern == '*':
                    matching_files = [
                        f for f in os.listdir('.')
                        if pattern.match(f)
                    ]
                else:
                    matching_files = [
                        f for f in os.listdir('.')
                        if pattern.match(f) and f.endswith(extension_pattern)
                    ]

                for old_file in matching_files:
                    # 使用正则替换
                    match = pattern.match(old_file)
                    if match:
                        prefix, suffix = match.groups()
                        new_file = f'{prefix}S{new_season:02d}E{new_episode:02d}{suffix}'

                        if os.path.exists(old_file):
                            rename_list.append((old_file, new_file))
                            self.rename_list.append((old_file, new_file))

            # 显示预览
            if rename_list:
                # 配置橙色标签
                self.preview_text.tag_configure('rename_preview_right', foreground='orange')

                for old, new in rename_list:
                    # 插入原文件名（默认颜色）
                    self.preview_text.insert(END, old)
                    # 插入箭头（默认颜色）
                    self.preview_text.insert(END, " → ")
                    # 插入新文件名（橙色）
                    self.preview_text.insert(END, new, 'rename_preview_right')
                    self.preview_text.insert(END, "\n")

                self.rename_button.config(state=NORMAL)
            else:
                self.preview_text.insert(END, "未找到匹配的文件")
                self.toast.show(
                    title="提示",
                    message="未找到匹配的文件",
                    duration=3000,
                    bootstyle="warning"
                )

        except ValueError as e:
            self.toast.show(
                title="错误",
                message=f"请输入有效的数字：{str(e)}",
                duration=3000,
                bootstyle="danger"
            )
        except Exception as e:
            self.toast.show(
                title="未知错误",
                message=str(e),
                duration=3000,
                bootstyle="danger"
            )



    def rename_files(self):
        """
        执行文件重命名
        """
        try:
            # 执行重命名
            for old_file, new_file in self.rename_list:
                os.rename(old_file, new_file)

            # 使用自定义 Toast 通知
            self.toast.show(
                title="重命名完成",
                message=f"成功重命名 {len(self.rename_list)} 个文件",
                duration=3000,  # 3秒后自动消失
                bootstyle="success"  # 使用成功样式
            )

            # 清空预览和重命名列表
            self.preview_text.delete('1.0', END)
            self.rename_list = []
            self.rename_button.config(state=DISABLED)

        except Exception as e:
            # 对于错误，仍然使用消息框
            messagebox.showerror("重命名错误", str(e))



def main():
    root = ttk.Window(themename="litera")
    app = FileRenamerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

'''
打包命令：
pyinstaller --onefile --windowed episode_renamer_extended.py -i E:\Pro_PY\pyexe\ico\episode_renamer.ico
'''
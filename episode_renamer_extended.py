import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, scrolledtext
import os
import sys
from filelock import FileLock
import tempfile
import json
import win32gui
import win32con

from episode_renamer import FileRenamerApp


class ExtendedFileRenamerApp(FileRenamerApp):
    def list_current_directory_files(self, filter_letter=None):
        """列出当前目录下的文件，可选择按首字母过滤"""
        try:
            # 清空之前的选中文件列表（除非在过滤模式）
            if not filter_letter:
                self.selected_files = []
            # 获取扩展名
            extension = self.extension_entry.get().strip()
            # 获取所有文件和文件夹
            all_items = os.listdir('.')
            # 分离文件夹和文件
            folders = [item for item in all_items if os.path.isdir(item)]
            files = [item for item in all_items if os.path.isfile(item)]
            # 当扩展名为 * 或空时，匹配所有文件
            if extension == '*' or extension == '':
                current_files = files
            else:
                # 确保扩展名以点开头
                extension = extension if extension.startswith('.') else '.' + extension
                current_files = [f for f in files if f.endswith(extension)]


            # 应用首字母过滤
            if filter_letter:
                import pypinyin
                import re
                filter_letter = filter_letter.lower()

                # 过滤文件夹
                filtered_folders = []
                for folder in folders:
                    folder_lower = folder.lower()
                    # 1. 检查文件名首字母
                    if folder_lower.startswith(filter_letter):
                        filtered_folders.append(folder)
                    # 2. 检查中文拼音首字母
                    elif folder and '\u4e00' <= folder[0] <= '\u9fff':  # 是中文字符
                        try:
                            pinyin = pypinyin.lazy_pinyin(folder[0])[0]
                            if pinyin.lower().startswith(filter_letter):
                                filtered_folders.append(folder)
                        except:
                            pass
                    # 3. 检查文件名中的单词首字母
                    else:
                        # 分割文件名成单词
                        words = re.findall(r'\b\w+\b', folder)
                        for word in words:
                            if word and word[0].lower() == filter_letter:
                                filtered_folders.append(folder)
                                break

                # 过滤文件
                filtered_files = []
                for file in current_files:
                    file_lower = file.lower()
                    # 1. 检查文件名首字母
                    if file_lower.startswith(filter_letter):
                        filtered_files.append(file)
                    # 2. 检查中文拼音首字母
                    elif file and '\u4e00' <= file[0] <= '\u9fff':  # 是中文字符
                        try:
                            pinyin = pypinyin.lazy_pinyin(file[0])[0]
                            if pinyin.lower().startswith(filter_letter):
                                filtered_files.append(file)
                        except:
                            pass
                    # 3. 检查文件名中的单词首字母
                    else:
                        # 分割文件名成单词
                        words = re.findall(r'\b\w+\b', file)
                        for word in words:
                            if word and word[0].lower() == filter_letter:
                                filtered_files.append(file)
                                break

                folders = filtered_folders
                current_files = filtered_files

            # 清空预览区
            self.preview_text.delete('1.0', END)
            # 配置字体和标签
            self.preview_text.configure(font=('Microsoft YaHei Mono', 13))
            # 配置标签样式
            self.preview_text.tag_configure('selected', background='lightblue')
            self.preview_text.tag_configure('folder', background='#FFF9C4', foreground='blue')
            self.preview_text.tag_configure('file', foreground='black')
            self.preview_text.tag_configure('parent_dir', background='#E0E0E0', foreground='green')
            # 如果不在根目录，添加返回上一级目录选项
            current_path = os.getcwd()
            if current_path != os.path.splitdrive(current_path)[0] + os.sep:
                self.preview_text.insert(END, "返回<<上一级目录\n", 'parent_dir')
                # 为返回上一级目录添加点击事件
                start_index = self.preview_text.search("返回<<上一级目录", "1.0", END)
                if start_index:
                    end_index = f"{start_index}+{len('返回<<上一级目录')}c"
                    tag_name = "parent_dir_tag"
                    self.preview_text.tag_add(tag_name, start_index, end_index)
                    self.preview_text.tag_bind(tag_name, '<Button-1>', self.handle_parent_dir_click)
                    # 添加鼠标悬停效果
                    self.preview_text.tag_bind(tag_name, '<Enter>',
                                               lambda e, tag=tag_name: self.preview_text.tag_configure(tag,
                                                                                                       underline=True))
                    self.preview_text.tag_bind(tag_name, '<Leave>',
                                               lambda e, tag=tag_name: self.preview_text.tag_configure(tag,
                                                                                                       underline=False))
            # 显示过滤状态（如果有）
            if filter_letter:
                self.preview_text.insert(END, f"[过滤中] 首字母: {filter_letter}\n", 'selected')
            # 如果有文件，显示文件列表
            if folders or current_files:
                # 对文件进行排序
                folders.sort()
                current_files.sort()
                # 清空标签映射
                self.file_tags = {}
                self.file_tag_indexes = {}
                # 显示文件夹
                for folder in folders:
                    self.preview_text.insert(END, f" {folder}\n", 'folder')
                    # 为文件夹添加点击事件
                    start_index = self.preview_text.search(folder, "1.0", END)
                    if start_index:
                        end_index = f"{start_index}+{len(folder)}c"
                        tag_name = f"folder_{folder}"
                        self.preview_text.tag_add(tag_name, start_index, end_index)
                        self.preview_text.tag_bind(tag_name, '<Button-1>',
                                                   lambda e, path=folder: self.handle_folder_click(path))
                        # 添加鼠标悬停效果
                        self.preview_text.tag_bind(tag_name, '<Enter>',
                                                   lambda e, tag=tag_name: self.preview_text.tag_configure(tag,
                                                                                                           underline=True))
                        self.preview_text.tag_bind(tag_name, '<Leave>',
                                                   lambda e, tag=tag_name: self.preview_text.tag_configure(tag,
                                                                                                           underline=False))
                # 显示文件
                for file in current_files:
                    self.preview_text.insert(END, f"{file}\n", 'file')
                    # 为文件添加标签和点击事件
                    tag_name = f"file_{file}"
                    self.file_tags[tag_name] = file
                    start_index = self.preview_text.search(file, "1.0", END)
                    if start_index:
                        end_index = f"{start_index}+{len(file)}c"
                        self.file_tag_indexes[tag_name] = (start_index, end_index)
                        self.preview_text.tag_add(tag_name, start_index, end_index)
                        self.preview_text.tag_bind(tag_name, '<Button-1>',
                                                   lambda e, t=tag_name: self.on_file_click(e, t))

                        # 如果该文件在选中列表中，添加选中样式
                        if file in self.selected_files:
                            self.preview_text.tag_add('selected', start_index, end_index)
                if folders or current_files:
                    total_files = len(current_files)
                    selected_files = len(self.selected_files)
                    self.update_file_counter(total_files, selected_files)
                else:
                    self.update_file_counter(0, 0)
            else:
                if filter_letter:
                    self.preview_text.insert(END, f"没有找到首字母为 '{filter_letter}' 的文件或文件夹")
                else:
                    self.preview_text.insert(END, "当前目录没有匹配的文件")
        except Exception as e:
            self.preview_text.insert(END, f"列出文件时发生错误：{str(e)}")
            self.update_file_counter(0, 0)
            import traceback
            traceback.print_exc()

    def update_file_counter(self, total_files, selected_files):
        """更新文件计数显示"""
        self.file_counter_label.configure(
            text=f"总文件: {total_files} | 选中: {selected_files}"
        )
    def handle_parent_dir_click(self, event=None):
        """处理返回上一级目录事件"""
        try:
            # 切换到上一级目录
            parent_dir = os.path.dirname(os.getcwd())
            os.chdir(parent_dir)

            # 更新目录标签
            self.current_dir = parent_dir
            self.dir_entry.configure(state="normal")
            self.dir_entry.delete(0, END)
            self.dir_entry.insert(0, parent_dir)
            self.dir_entry.configure(state="readonly")

            # 保存最后选择的目录
            self.save_last_directory(parent_dir)

            # 重新列出文件
            self.list_current_directory_files()

        except Exception as e:
            messagebox.showerror("错误", f"无法返回上一级目录：{str(e)}")

    def handle_folder_click(self, folder_path):
        """处理文件夹点击事件"""
        try:
            # 切换到选定的文件夹
            full_path = os.path.abspath(folder_path)
            os.chdir(full_path)

            # 更新目录标签
            self.current_dir = full_path
            self.dir_entry.configure(state="normal")
            self.dir_entry.delete(0, END)
            self.dir_entry.insert(0, full_path)
            self.dir_entry.configure(state="readonly")

            # 保存最后选择的目录
            self.save_last_directory(full_path)

            # 重新列出文件
            self.list_current_directory_files()

        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹：{str(e)}")

    def on_file_click(self, event, tag_name):
        """处理文件点击事件"""
        # 文件夹不执行点击事件
        if tag_name.startswith('folder_'):
            return

        # 从文件标签映射中获取文件名
        filename = self.file_tags.get(tag_name)
        if not filename:
            return

        # 获取标签的索引
        start_index, end_index = self.file_tag_indexes.get(tag_name, (None, None))
        if start_index is None or end_index is None:
            return

        # 检查是否已经选中
        if filename in self.selected_files:
            # 如果已选中，则取消选中
            self.selected_files.remove(filename)
            self.preview_text.tag_remove('selected', start_index, end_index)
        else:
            # 添加到选中列表
            self.selected_files.append(filename)
            self.preview_text.tag_add('selected', start_index, end_index)

        # 更新文件计数
        total_files = len([f for f in os.listdir('.') if os.path.isfile(f)])
        selected_files = len(self.selected_files)
        self.update_file_counter(total_files, selected_files)

    def __init__(self, master):
        """初始化方法"""
        # 调用父类初始化方法
        super().__init__(master)

        # 加载上次选择的目录
        self.current_dir = self.load_last_directory()
        os.chdir(self.current_dir)

        # 移除原有的pack布局
        for widget in self.main_container.winfo_children():
            widget.pack_forget()

        # 配置主容器为grid布局
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=1)

        # 标题
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='ew')

        # 左侧预览区
        self.preview_frame = ttk.LabelFrame(
            self.main_container,
            text="文件列表",
            bootstyle=INFO,
            padding=10
        )
        self.preview_frame.grid(row=1, column=0, padx=(0, 5), pady=5, sticky='nsew')

        # 当前目录标签
        dir_frame = ttk.Frame(self.preview_frame)
        dir_frame.pack(side=TOP, fill=X, padx=10, pady=(0, 5))
        ttk.Label(dir_frame, text="当前目录:", bootstyle=SECONDARY).pack(side=LEFT)
        # 使用Entry控件代替Label，以允许文本选择和复制
        self.dir_entry = ttk.Entry(dir_frame, width=50)
        self.dir_entry.pack(side=LEFT, padx=(5, 0), fill=X, expand=YES)
        self.dir_entry.insert(0, self.current_dir)
        self.dir_entry.configure(state="readonly")  # 只读模式，但允许复制

        self.preview_text = scrolledtext.ScrolledText(
            self.preview_frame,
            font=('Microsoft YaHei Mono', 11),
            wrap=tk.WORD
        )
        self.preview_text.pack(fill=BOTH, expand=YES)

        # 创建计数器框架和标签（在预览文本框之后）
        counter_frame = ttk.Frame(self.preview_frame)
        counter_frame.pack(side=BOTTOM, fill=X, padx=5, pady=5)

        # 文件计数标签
        self.file_counter_label = ttk.Label(
            counter_frame,
            text="总文件: 0 | 选中: 0",
            bootstyle=SECONDARY
        )
        self.file_counter_label.pack(side=LEFT)

        # 右侧主功能区
        right_container = ttk.Frame(self.main_container)
        right_container.grid(row=1, column=1, padx=(5, 0), pady=5, sticky='nsew')

        # 目录和扩展名选择区域
        dir_frame = ttk.Frame(right_container)
        dir_frame.pack(fill=X, pady=5)

        # 扩展名过滤区域（单独一行）
        extension_frame = ttk.Frame(right_container)
        extension_frame.pack(fill=X, pady=5)

        extension_label = ttk.Label(
            extension_frame,
            text="扩展名全局过滤：",
            bootstyle=DANGER
        )
        extension_label.pack(side=LEFT, padx=(10, 5))

        self.extension_entry = ttk.Entry(extension_frame, width=8)
        self.extension_entry.pack(side=LEFT, padx=(0, 10))
        self.extension_entry.insert(0, "*")

        # 刷新和选择文件夹按钮区域
        button_frame = ttk.Frame(right_container)
        button_frame.pack(fill=X, pady=5)

        # 选择文件夹按钮
        self.select_dir_button = ttk.Button(
            button_frame,
            text="切换目录",
            command=self.select_directory,
            bootstyle=PRIMARY,
            width=16
        )
        self.select_dir_button.pack(side=LEFT, padx=10)
        # 刷新按钮
        self.refresh_dir_button = ttk.Button(
            button_frame,
            text="刷新/取消",
            command=self.list_current_directory_files,
            bootstyle=SUCCESS,
            width=18
        )
        self.refresh_dir_button.pack(side=LEFT, padx=5)

        # 首字母过滤区域
        filter_frame = ttk.LabelFrame(
            right_container,
            text="首字母过滤",
            bootstyle=WARNING,
            padding=10
        )
        filter_frame.pack(fill=X, pady=5)
        # 添加首字母输入框和过滤按钮
        filter_row = ttk.Frame(filter_frame)
        filter_row.pack(fill=X, pady=5)
        ttk.Label(filter_row, text="首字母:").pack(side=LEFT, padx=(0, 5))
        self.filter_letter_entry = ttk.Entry(filter_row, width=10)
        self.filter_letter_entry.pack(side=LEFT, padx=(0, 10))
        # 添加过滤和清除按钮
        filter_btn_frame = ttk.Frame(filter_frame)
        filter_btn_frame.pack(fill=X, pady=5)
        self.filter_button = ttk.Button(
            filter_btn_frame,
            text="应用过滤",
            command=self.apply_letter_filter,
            bootstyle=WARNING,
            width=15
        )
        self.filter_button.pack(side=LEFT, expand=YES, padx=10)
        self.clear_filter_button = ttk.Button(
            filter_btn_frame,
            text="清除过滤",
            command=self.clear_letter_filter,
            bootstyle=SECONDARY,
            width=15
        )
        self.clear_filter_button.pack(side=LEFT, expand=YES, padx=10)
        # 存储过滤前的文件列表和当前过滤状态
        self.original_files = []
        self.is_filtered = False
        # 绑定回车键事件
        self.filter_letter_entry.bind('<Return>', lambda event: self.apply_letter_filter())

        # 季号集号调整区域
        season_episode_frame = ttk.LabelFrame(
            right_container,
            text="季号集号调整",
            bootstyle=INFO,
            padding=14
        )
        season_episode_frame.pack(fill=X, pady=5)

        # 原文件信息区域
        old_info_frame = ttk.LabelFrame(
            season_episode_frame,
            text="原文件信息",
            bootstyle=PRIMARY,
            padding=10
        )
        old_info_frame.pack(fill=X, padx=5, pady=5)

        # 原文件季号
        old_season_row = ttk.Frame(old_info_frame)
        old_season_row.pack(fill=X, pady=5)

        ttk.Label(old_season_row, text="原季号:").pack(side=LEFT, padx=(0, 5))
        self.old_season_entry = ttk.Entry(old_season_row, width=10)
        self.old_season_entry.pack(side=LEFT, padx=(0, 10))

        # 原文件集号起始
        old_episode_start_row = ttk.Frame(old_info_frame)
        old_episode_start_row.pack(fill=X, pady=5)

        ttk.Label(old_episode_start_row, text="集号起始:").pack(side=LEFT, padx=(0, 5))
        self.old_episode_start = ttk.Entry(old_episode_start_row, width=10)
        self.old_episode_start.pack(side=LEFT, padx=(0, 10))

        # 原文件集号截止
        old_episode_end_row = ttk.Frame(old_info_frame)
        old_episode_end_row.pack(fill=X, pady=5)

        ttk.Label(old_episode_end_row, text="集号截止:[不填默认999]").pack(side=LEFT, padx=(0, 5))
        self.old_episode_end = ttk.Entry(old_episode_end_row, width=10)
        self.old_episode_end.pack(side=LEFT, padx=(0, 10))

        # 新文件信息区域
        new_info_frame = ttk.LabelFrame(
            season_episode_frame,
            text="新文件信息",
            bootstyle=SUCCESS,
            padding=10
        )
        new_info_frame.pack(fill=X, padx=5, pady=5)

        # 新文件季号
        new_season_row = ttk.Frame(new_info_frame)
        new_season_row.pack(fill=X, pady=5)

        ttk.Label(new_season_row, text="新季号:").pack(side=LEFT, padx=(0, 5))
        self.new_season_entry = ttk.Entry(new_season_row, width=10)
        self.new_season_entry.pack(side=LEFT, padx=(0, 10))

        # 新文件集号起始
        new_episode_start_row = ttk.Frame(new_info_frame)
        new_episode_start_row.pack(fill=X, pady=5)

        ttk.Label(new_episode_start_row, text="集号起始:").pack(side=LEFT, padx=(0, 5))
        self.new_episode_start = ttk.Entry(new_episode_start_row, width=10)
        self.new_episode_start.pack(side=LEFT, padx=(0, 10))

        # 新文件集号截止
        new_episode_end_row = ttk.Frame(new_info_frame)
        new_episode_end_row.pack(fill=X, pady=5)

        ttk.Label(new_episode_end_row, text="集号截止:[不填自动跟随]").pack(side=LEFT, padx=(0, 5))
        self.new_episode_end = ttk.Entry(new_episode_end_row, width=10)
        self.new_episode_end.pack(side=LEFT, padx=(0, 10))

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

        # 添加字符串替换和前缀区域
        self.add_string_replacement_section(right_container)

        # 添加选中文件列表
        self.selected_files = []

        # 绑定扩展名输入框的事件
        self.extension_entry.bind('<FocusOut>', lambda event: self.list_current_directory_files())
        # 添加点击其他位置取消焦点的绑定
        self.master.bind('<Button-1>', self.handle_click_outside)

        # 确保所有UI元素都创建完成后再列出文件
        self.master.after(100, self.list_current_directory_files)

    # 2. 添加首字母过滤相关方法
    def apply_letter_filter(self):
        """应用首字母过滤"""
        try:
            filter_letter = self.filter_letter_entry.get().strip().lower()

            if not filter_letter:
                self.toast.show(
                    title="提示",
                    message="请输入要过滤的首字母",
                    duration=3000,
                    bootstyle="warning"
                )
                return

            # 如果当前没有过滤，则保存原始文件列表
            if not self.is_filtered:
                self.original_files = self.selected_files.copy() if self.selected_files else []

            # 重新列出目录内容，但应用过滤
            self.list_current_directory_files(filter_letter=filter_letter)
            self.is_filtered = True

        except Exception as e:
            messagebox.showerror("过滤错误", str(e))

    def clear_letter_filter(self):
        """清除首字母过滤"""
        if self.is_filtered:
            self.filter_letter_entry.delete(0, END)
            self.is_filtered = False
            self.list_current_directory_files()

            # 如果有选中的文件，恢复原始选中状态
            if self.original_files:
                # 清除当前选择
                self.selected_files = []
                # 重新显示并选中之前选中的文件
                for file in self.original_files:
                    if os.path.exists(file):
                        tag_name = f"file_{file}"
                        if tag_name in self.file_tag_indexes:
                            start_index, end_index = self.file_tag_indexes[tag_name]
                            self.selected_files.append(file)
                            self.preview_text.tag_add('selected', start_index, end_index)

    def handle_click_outside(self, event):
        """处理点击其他位置的事件"""
        # 获取当前获得焦点的控件
        focused_widget = self.master.focus_get()

        # 检查是否需要取消焦点
        if focused_widget == self.extension_entry:
            # 检查点击的控件是否是输入框或按钮
            clicked_widget = event.widget

            # 定义不需要取消焦点的控件类型
            ignore_widgets = [
                ttk.Entry,  # 所有输入框
                ttk.Button,  # 所有按钮
                ttk.Combobox,  # 下拉框
            ]

            # 如果点击的不是这些控件，则取消焦点
            if not any(isinstance(clicked_widget, widget_type) for widget_type in ignore_widgets):
                self.master.focus_set()

    def select_directory(self):
        """选择文件夹"""
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            self.current_dir = selected_dir
            self.dir_entry.configure(state="normal")
            self.dir_entry.delete(0, END)
            self.dir_entry.insert(0, self.current_dir)
            self.dir_entry.configure(state="readonly")
            os.chdir(self.current_dir)

            # 保存最后选择的目录
            self.save_last_directory(self.current_dir)

            # 列出新目录下的文件
            self.list_current_directory_files()

    def rearrange_directory_section(self):
        # 找到并重新布置目录选择区域
        for frame in self.main_container.winfo_children():
            if isinstance(frame, ttk.Frame):
                # 检查是否是目录选择区域
                children = frame.winfo_children()
                if len(children) > 1 and isinstance(children[0], ttk.Label):
                    # 清除原有布局
                    for child in children:
                        child.pack_forget()

                    # 重新布置
                    self.dir_label = ttk.Label(frame, text="当前目录：", bootstyle=SECONDARY)
                    self.dir_label.pack(side=LEFT, padx=10)

                    # 添加扩展名输入
                    extension_label = ttk.Label(
                        frame,
                        text="扩展名全局过滤",
                        bootstyle=DANGER  # 使用 DANGER 样式替代 outline
                    )
                    extension_label.pack(side=LEFT, padx=(10, 5))

                    self.extension_entry = ttk.Entry(frame, width=20)
                    self.extension_entry.pack(side=LEFT, padx=(0, 10))
                    self.extension_entry.insert(0, "*")

                    # 选择文件夹按钮
                    self.select_dir_button = ttk.Button(
                        frame,
                        text="切换目录",
                        command=self.select_directory,
                        bootstyle=PRIMARY,
                        width=8
                    )
                    self.select_dir_button.pack(side=CENTER, padx=6)

                    break

    def add_string_replacement_section(self, parent):
        # 字符串替换和前缀区域
        string_frame = ttk.LabelFrame(
            parent,
            text="字符串替换与前缀",
            bootstyle=SECONDARY,
            padding=10
        )
        string_frame.pack(fill=X, pady=5)

        # 替换前字符串
        replace_before_row = ttk.Frame(string_frame)
        replace_before_row.pack(fill=X, pady=5)

        ttk.Label(replace_before_row, text="替换前:").pack(side=LEFT, padx=(0, 5))
        self.replace_before_entry = ttk.Entry(replace_before_row, width=50)
        self.replace_before_entry.pack(side=LEFT, padx=(0, 10))

        # 替换后字符串
        replace_after_row = ttk.Frame(string_frame)
        replace_after_row.pack(fill=X, pady=5)

        ttk.Label(replace_after_row, text="替换后:").pack(side=LEFT, padx=(0, 5))
        self.replace_after_entry = ttk.Entry(replace_after_row, width=50)
        self.replace_after_entry.pack(side=LEFT, padx=(0, 10))

        # 前缀字符串
        prefix_row = ttk.Frame(string_frame)
        prefix_row.pack(fill=X, pady=5)

        ttk.Label(prefix_row, text="添加前缀:").pack(side=LEFT, padx=(0, 5))
        self.prefix_entry = ttk.Entry(prefix_row, width=50)
        self.prefix_entry.pack(side=LEFT, padx=(0, 10))

        # 替换和前缀操作按钮
        btn_frame = ttk.Frame(string_frame)
        btn_frame.pack(fill=X, pady=5)

        self.replace_preview_button = ttk.Button(
            btn_frame,
            text="预览替换",
            command=self.preview_string_replacement,
            bootstyle=INFO,
            width=15
        )
        self.replace_preview_button.pack(side=LEFT, expand=YES, padx=10)

        self.replace_execute_button = ttk.Button(
            btn_frame,
            text="执行替换",
            command=self.execute_string_replacement,
            bootstyle=DANGER,
            state=DISABLED,
            width=15
        )
        self.replace_execute_button.pack(side=LEFT, expand=YES, padx=10)

        # 存储替换后的文件列表
        self.replacement_list = []

    def preview_rename(self):
        # 调用父类的预览重命名方法，并传入扩展名
        super().preview_rename()

    def preview_string_replacement(self):
        """预览字符串替换和前缀添加"""
        try:
            # 获取扩展名
            extension = self.extension_entry.get().strip()

            # 获取当前目录下的所有文件
            current_files = self.selected_files if self.selected_files else [f for f in os.listdir('.')]

            # 过滤文件
            if extension != '*' and extension != '':
                extension = extension if extension.startswith('.') else '.' + extension
                current_files = [f for f in current_files if f.endswith(extension)]

            # 重置预览和执行按钮状态
            self.preview_text.delete('1.0', END)
            self.replace_execute_button.config(state=DISABLED)
            self.replacement_list = []

            # 获取替换和前缀信息 - 不去除空格
            replace_before = self.replace_before_entry.get()
            replace_after = self.replace_after_entry.get()
            prefix = self.prefix_entry.get().strip()  # 前缀仍然去除空格

            # 如果没有替换和前缀，提示
            if not replace_before and not prefix:
                self.toast.show(
                    title="提示",
                    message="请输入替换前字符串或前缀",
                    duration=3000,
                    bootstyle="warning"
                )
                return

            # 执行替换和前缀添加
            replacement_list = []
            for filename in current_files:
                new_filename = filename

                # 执行字符串替换 - 保留空格
                if replace_before:
                    new_filename = new_filename.replace(replace_before, replace_after)

                # 添加前缀
                if prefix:
                    new_filename = prefix + new_filename

                # 如果文件名发生变化，添加到列表
                if new_filename != filename:
                    replacement_list.append((filename, new_filename))

            # 显示预览
            if replacement_list:
                # 配置橙色标签
                self.preview_text.tag_configure('replace_preview_right', foreground='orange')

                for old, new in replacement_list:
                    # 插入原文件名（默认颜色）
                    self.preview_text.insert(END, old)
                    # 插入箭头（默认颜色）
                    self.preview_text.insert(END, " → ")
                    # 插入新文件名（橙色）
                    self.preview_text.insert(END, new, 'replace_preview_right')
                    self.preview_text.insert(END, "\n")

                self.replace_execute_button.config(state=NORMAL)
                self.replacement_list = replacement_list
            else:
                self.preview_text.insert(END, "未找到需要替换的文件")
                self.toast.show(
                    title="提示",
                    message="未找到需要替换的文件",
                    duration=3000,
                    bootstyle="warning"
                )

        except Exception as e:
            messagebox.showerror("错误", str(e))

    def execute_string_replacement(self):
        """执行字符串替换和前缀添加"""
        try:
            # 执行重命名
            for old_file, new_file in self.replacement_list:
                os.rename(old_file, new_file)

            # 使用自定义 Toast 通知
            self.toast.show(
                title="替换完成",
                message=f"成功替换 {len(self.replacement_list)} 个文件",
                duration=3000,
                bootstyle="success"
            )

            # 清空预览和重命名列表
            self.preview_text.delete('1.0', END)
            self.replacement_list = []
            self.replace_execute_button.config(state=DISABLED)

            # 刷新文件列表
            self.list_current_directory_files()

        except Exception as e:
            messagebox.showerror("重命名错误", str(e))





class WindowInfo:
    def __init__(self):
        self.hwnd = None  # 窗口句柄

    def save_window_info(self, hwnd):
        """保存窗口信息到临时文件"""
        info = {'hwnd': hwnd}
        info_file = os.path.join(tempfile.gettempdir(), 'episode_renamer_info.json')
        with open(info_file, 'w') as f:
            json.dump(info, f)

    def load_window_info(self):
        """加载窗口信息"""
        info_file = os.path.join(tempfile.gettempdir(), 'episode_renamer_info.json')
        try:
            with open(info_file, 'r') as f:
                info = json.load(f)
                return info.get('hwnd')
        except:
            return None

    def activate_existing_window(self):
        """激活已存在的窗口"""
        hwnd = self.load_window_info()
        if hwnd:
            try:
                # 恢复窗口（如果最小化）
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # 将窗口置于前台
                win32gui.SetForegroundWindow(hwnd)
                return True
            except:
                return False
        return False


def check_singleton():
    """检查是否已有实例在运行"""
    lock_file = os.path.join(tempfile.gettempdir(), 'episode_renamer.lock')
    lock = FileLock(lock_file)
    try:
        lock.acquire(timeout=0.1)
        return lock
    except:
        return None


def save_window_handle(root):
    """保存窗口句柄"""
    window_info = WindowInfo()
    window_info.save_window_info(root.winfo_id())


def main(initial_path=None):
    # 检查是否已有实例在运行
    window_info = WindowInfo()
    lock = check_singleton()

    if not lock:
        # 尝试激活已存在的窗口
        if window_info.activate_existing_window():
            return
        else:
            import tkinter.messagebox as msgbox
            msgbox.showwarning("警告", "程序已经在运行中！")
            return

    try:
        root = ttk.Window(themename="litera")
        app = ExtendedFileRenamerApp(root)

        # 窗口创建后保存窗口句柄
        root.after(100, lambda: save_window_handle(root))

        if initial_path and os.path.exists(initial_path):
            if os.path.isfile(initial_path):
                initial_dir = os.path.dirname(os.path.abspath(initial_path))
            else:
                initial_dir = os.path.abspath(initial_path)

            app.current_dir = initial_dir
            os.chdir(initial_dir)
            app.dir_entry.configure(state="normal")
            app.dir_entry.delete(0, END)
            app.dir_entry.insert(0, initial_dir)
            app.dir_entry.configure(state="readonly")
            app.list_current_directory_files()

        root.mainloop()
    finally:
        # 程序结束时清理
        if lock:
            lock.release()
        # 删除窗口信息文件
        try:
            info_file = os.path.join(tempfile.gettempdir(), 'episode_renamer_info.json')
            if os.path.exists(info_file):
                os.remove(info_file)
        except:
            pass


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()

'''
打包命令：
pyinstaller --onefile --windowed episode_renamer_extended.py -i E:\Pro_PY\pyexe\ico\episode_renamer.ico
'''
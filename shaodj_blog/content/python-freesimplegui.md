Title: 使用 FreeSimpleGUI 定制图形界面
Slug: python-freesimplegui
Date: 2025-02-06 17:18
Category: 编程
Tags: blog, python, gui, tkinter

## 什么是FreeSimpleGUI？
**FreeSimpleGUI**是一个开源的图形用户界面库，旨在提供一个简单、易用的GUI解决方案。 它简化了窗口和元素的创建过程，通过一个简洁的布局定义系统，支持多种流行的 GUI 框架，包括 tkinter、Qt、WxPython 和 Remi。它通过封装这些框架的常用功能，提供了更简洁的 API，让你专注于应用逻辑而非繁杂的UI细节。

## FreeSimpleGUI的特点

- 简单易用：FreeSimpleGUI的API设计非常简单易用，任何人都可以轻松地使用它来创建GUI应用程序。

- 免费：FreeSimpleGUI是完全免费的，不需要任何付费许可证，可以自由地使用和分发。

- 跨平台：FreeSimpleGUI支持多种平台，包括Windows、MacOS和Linux等。

- 高性能：FreeSimpleGUI具有高性能，能够快速地渲染和响应用户交互。

- 灵活：FreeSimpleGUI提供了多种自定义选项，允许开发者根据需要进行自定义和调整。


## 技术应用示例
```python
import FreeSimpleGUI as sg
from glob import glob

version = 0.8

# 界面布局
sg.theme('TanBlue')  # 图形界面布局
 
layout = [
    [sg.Text("重要资料目录夹: "), 
     sg.In(size=(35, 1), enable_events=True, key="_FOLDER_"),
     sg.FolderBrowse()],
    [sg.Text("水印大小: "),
     sg.Slider(range=(30, 100), resolution=10, default_value=60,
        size=(12, 15), border_width=1, text_color='navy',
        orientation='horizontal', key='_SCALE_')],
    [sg.Text('水印文字:'), 
     sg.InputText(size=(20, 1), key='_WORDS_')],
    [sg.Button('OK'),  sg.Button('Exit')],
]
 
types = ["png", "jpg", "jpeg"]
 
window = sg.Window(f'又拍云水印系统 v{version} -悟空', layout).Finalize()
while True:
    jpg_and_pngs = []
    event, values = window.read()
    if event in (None, 'Exit'):
        break
    elif event in (None, 'OK'):
        if values['_FOLDER_'] != "":
            if values['_WORDS_'] == "":
                sg.popup("水印文字不能为空!")
                continue
            for type in types:
                files = f"{values['_FOLDER_']}/*.{type}"
                this_type_files = glob(files)
                jpg_and_pngs += this_type_files
            if len(jpg_and_pngs) == 0:
                sg.popup("没有发现图片!")
                continue
            else:
                for f in jpg_and_pngs:
                    if IsValidImage(f):
                        add_mark_png(f, values['_WORDS_'], values['_SCALE_'])
                    else:
                        sg.popup("图片格式与后缀名不符!")
                        continue
            sg.popup("处理完毕!")
        else:
            sg.popup("目录不能为空!")
window.close()
```
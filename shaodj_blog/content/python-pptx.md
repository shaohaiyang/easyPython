Title: 使用 python-pptx 库制作PowerPoint
Slug: python-pptx-powerpoint
Date: 2025-02-05 17:38
Category: 编程
Tags: blog, python, ppt, pptx

## python-pptx 库简介
[python-pptx](https://python-pptx.readthedocs.io/) 是一个用于创建和修改 PowerPoint (.pptx) 文件的 Python 库。它提供了丰富的功能，使用户能够方便地生成演示文稿，并且可以进行各种格式的自定义。

## 特性
- 创建新演示文稿：可以从零开始创建新的 PowerPoint 文件。

- 修改现有文件：支持打开和编辑已有的 .pptx 文件。

- 添加幻灯片：可以轻松地添加、删除和重新排列幻灯片。

- 文本和图形：支持插入各种文本框、图形、图片和表格。

- 自定义格式：可以设置字体、颜色、大小等样式。

- 支持图表：可以插入和自定义图表。

## 注意事项：
**python-pptx <u>本身不支持</u>** 复杂的动画效果，如果需要更复杂的动画，可以在生成的 PowerPoint 文件中手动设置。

---

## 基本用法
以下是一个简单的示例，展示如何使用 python-pptx 创建一个包含文本的幻灯片：
```python

from pptx import Presentation
from pptx.util import Inches
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR

# 创建一个演示文稿对象
prs = Presentation()

# 添加一个标题幻灯片
slide_layout = prs.slide_layouts[0]  # 0 是标题幻灯片的布局
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]
title.text = "Python-pptx 示例"
subtitle.text = "创建包含基本要素和简单动画的PPT"

# 添加一个包含文本和图片的幻灯片
slide_layout = prs.slide_layouts[5]  # 5 是空白幻灯片的布局
slide = prs.slides.add_slide(slide_layout)

# 添加标题
title = slide.shapes.title
title.text = "文本和图片"

# 添加文本框
left = Inches(1)
top = Inches(1.5)
width = Inches(3)
height = Inches(1)
textbox = slide.shapes.add_textbox(left, top, width, height)
tf = textbox.text_frame
tf.text = "这是一个示例文本框。"
p = tf.add_paragraph()
p.text = "这是第二行文本。"

# 添加图片
left = Inches(4)
top = Inches(1.5)
height = Inches(2.5)
pic = slide.shapes.add_picture("demo.png", left, top, height=height)

# 添加一个包含表格的幻灯片
slide_layout = prs.slide_layouts[5]
slide = prs.slides.add_slide(slide_layout)

# 添加标题
title = slide.shapes.title
title.text = "表格示例"

# 添加表格
left = Inches(1)
top = Inches(1.5)
width = Inches(8)
height = Inches(2)
rows = 4
cols = 3
table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# 填充表格数据
table.cell(0, 0).text = "序号"
table.cell(0, 1).text = "名称"
table.cell(0, 2).text = "值"

for i in range(1, rows):
    table.cell(i, 0).text = str(i)
    table.cell(i, 1).text = f"项目 {i}"
    table.cell(i, 2).text = str(i * 10)

# 添加一个包含简单动画效果的幻灯片
slide_layout = prs.slide_layouts[5]
slide = prs.slides.add_slide(slide_layout)

# 添加标题
title = slide.shapes.title
title.text = "简单动画效果"

# 添加一个形状
left = Inches(1)
top = Inches(1.5)
width = Inches(2)
height = Inches(1)
shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
shape.text = "点击我！"

# 设置形状的填充颜色
fill = shape.fill
fill.solid()
fill.fore_color.rgb = RGBColor(0x1E, 0x90, 0xFF)  # 蓝色

# 保存演示文稿
prs.save("example_presentation.pptx")

print("PPT 文件已创建成功！")
```
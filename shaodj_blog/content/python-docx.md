Title: 使用 python-docx 创建 word 文件
Slug: python-pydocx
Date: 2025-02-01 10:52
Category: 编程
Tags: blog, python

代码示例展示了如何使用 `python-docx` 库创建和修改 Word 文件。

## 可运行代码
```python
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor 

template = "demo.docx"
name_placeholder = "<name>"
sex_placeholder = "<sex>" 

def new_doc(template="demo.docx"):
    doc = Document()
    
    # 设置 Normal 样式
    doc.styles["Normal"].font.name = "PingFang"
    doc.styles["Normal"]._element.rPr.rFonts.set(qn('w:eastAsia'), 'PingFang') 
    doc.styles["Normal"].font.color.rgb = RGBColor(255, 0, 0)
    doc.styles["Normal"].font.size = Pt(15)

    # 添加标题和段落
    doc.add_heading(f'段落标题:  欢迎! {name_placeholder} ({sex_placeholder}) ', level=0)

    p = doc.add_paragraph('段落正文: ')
    p.add_run('粗体').bold = True
    p.add_run(' and some ')
    p.add_run('斜体.').italic = True

    doc.add_heading('一级标题： Heading, level 1', level=1)
    doc.add_paragraph('引用段落：Intense quote', style='Intense Quote')
    doc.add_paragraph('first item in unordered list', style='List Bullet')
    doc.add_paragraph('first item in ordered list', style='List Number')

    # 添加图片
    doc.add_picture('test0.png', width=Inches(2.0))

    # 添加表格
    records = (
        (3, '101', '土豆'),
        (7, '422', '鸡蛋'),
        (4, '631', '西红柿')
    )
    table = doc.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = '数量'
    hdr_cells[1].text = 'Id'
    hdr_cells[2].text = '描述'
    
    for qty, id, desc in records:
        row_cells = table.add_row().cells
        row_cells[0].text = str(qty)
        row_cells[1].text = id
        row_cells[2].text = desc

    doc.add_page_break()
    doc.save(template)

def invite(template, name, sex):
    doc = Document(template)
    for para in doc.paragraphs:
        for run in para.runs:
            if name_placeholder in run.text:
                run.text = run.text.replace(name_placeholder, name)
            if sex_placeholder in run.text:
                sex = "先生" if sex == "男" else "女士"
                run.text = run.text.replace(sex_placeholder, sex)
    doc.save(f"{name}.docx")

# 创建新文档并替换占位符
new_doc(template)
invite(template, "东俊", "男")
```
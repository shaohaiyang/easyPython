Title: 使用 PyPDF 和 Pandoc 实现word/pdf转换
Slug: python-pypdf-pandoc
Date: 2025-02-01 15:04
Category: 编程
Tags: blog, python

代码示例展示了如何使用 `PyPDF` 和 `Pandoc` 实现word/pdf转换

关于[Pandoc的具体用法](https://medium.com/@daneallist/3-simple-ways-to-merge-word-documents-using-python-862112ff4152)

```python
from pypandoc import convert_file
from pathlib import Path
from PyPDF2 import PdfReader,PdfWriter 
unused = ('~', 'demo')

def find_doc_files(dir, type="docx"):
    return [file for file in Path(dir).rglob(f'*.{type}')
             if not file.name.startswith(unused)
    ]

def convert_pdf(infile, outfile):
    convert_file(
        infile, 'pdf', outfile, 
        extra_args=['--pdf-engine=weasyprint'])
    
def add_watermark(infile, watermark, outfile):
    old_file = PdfReader(infile)
    new_file = PdfWriter()

    for pageNum in range(0,len(old_file.pages)):
        page = old_file.pages[pageNum]
        page.merge_page(watermark)
        new_file.add_page(page)
        
    with open(outfile,"wb") as f:
        new_file.write(f)

if __name__ == "__main__":
    watermark_file = PdfReader("watermark.pdf")
    watermark = watermark_file.pages[0]
    
    file_list = find_doc_files(".", "docx")
    for file in file_list:
        name = Path(file).stem
        convert_pdf(file, f"{name}.pdf")
        add_watermark(file, watermark, f"{name}_mark.pdf")
```

## 代码分析

### 查找 docx 文件：
- find_doc_files 函数使用 Path.rglob 方法递归查找指定目录中的 DOCX 文件，排除以 unused 元组中指定的前缀开头的文件。

### PDF 转换：
- convert_pdf 函数使用 pypandoc 的 convert_file 方法将 docx 文件转换为 PDF，使用 WeasyPrint 作为 PDF 引擎。

### 添加水印：
- add_watermark 函数读取输入 PDF，使用 PyPDF2 将水印添加到每一页，并保存为新文件。

## 注意事项
### 依赖库安装：
确保已安装 pypandoc、PyPDF2 和 WeasyPrint。可以通过以下命令安装：
```bash
pip install pypandoc PyPDF2 WeasyPrint
```
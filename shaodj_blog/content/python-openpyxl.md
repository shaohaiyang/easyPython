Title: 使用 openpyxl 创建 Excel 文件
Slug: python-openpyxl
Date: 2025-01-31 18:00
Category: 编程
Tags: blog, python

代码示例展示了如何使用 `openpyxl` 库从文本文件中读取数据并将其写入Excel文件。

## 可运行代码

```python
import openpyxl

# 创建一个新的工作簿
wb = openpyxl.Workbook()

# 创建一个工作表并命名为 "人员名单"
wt = wb.create_sheet("人员名单", 0)

# 从文本文件读取数据并写入工作表
with open("memo.txt", "r", encoding='utf-8') as f:
    for idx, line in enumerate(f.readlines()):
        row = idx + 1  # Excel 行从 1 开始
        people = line.strip().split(",")
        if len(people) >= 2:  # 确保至少有两个元素
            name = people[0]
            sex = people[1]
            wt.cell(row=row, column=1, value=name)
            wt.cell(row=row, column=2, value=sex)
wb.save("测试名单.xlsx")
```

## 代码解释

### 创建工作簿和工作表：
- 使用 openpyxl.Workbook() 创建一个新的工作簿。
- create_sheet("人员名单", 0) 创建一个新的工作表并将其命名为 "人员名单"。

### 读取文件：
* 打开文本文件，确保使用正确的编码（如 UTF-8）。
* enumerate(f.readlines()) 用于逐行读取文件内容，并在循环中获得行索引。

### 处理数据：
* 使用 strip().split(",") 去除行首尾空白并根据逗号分隔字符串。
* 检查 people 列表的长度，确保至少有两个元素（姓名和性别）。

### 写入工作表：
* 使用 wt.cell(row=row, column=1, value=name) 将姓名写入第一列，性别写入第二列。

### 保存文件：
* 使用 wb.save("测试名单.xlsx") 保存工作簿。
* 注意，openpyxl 支持 .xlsx 格式，而不是 .xls。

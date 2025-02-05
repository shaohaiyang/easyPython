Title: 使用 PIL(pillow) 实现图片绘制 & 裁剪 & 水印
Slug: python-pillow-pil
Date: 2025-02-01 20:32
Category: 编程
Tags: blog, python

使用`PIL`代码实现了从图像中裁剪出一个`logo`，并将其作为水印添加到其他图像上。

```python
import os
from PIL import Image
from PIL import ImageDraw
from pathlib import Path

path = "/Users/apple/myDemo/Python39_Demos/image"

infile = os.path.join(path, "test0.png")
watermark = os.path.join(path, "../logo.png")  # 这里修复了路径
margin = 5

def crop_logo(infile, outfile):
    try:
        pyimg = Image.open(infile)
        width = pyimg.width
        height = pyimg.height
        print(f"图像的高和宽: {height}, {width}")
        logo = pyimg.crop((50, 50, 150, 150))
        logo.save(outfile)
    except Exception as e:
        print(f"裁剪 Logo 时出错: {e}")

def img_watermark(infile, waterfile, outfile):
    try:
        logo = Image.open(waterfile)
        image = Image.open(infile)
        x = image.width - logo.width - margin
        y = image.height - logo.height - margin
        
        image.paste(logo, (x, y))  # 使用 logo 作为掩码
        image.save(outfile)
    except Exception as e:
        print(f"添加水印时出错: {e}")

def draw_logo(outfile, text="python"):
    img = Image.new("RGBA", (400, 400), "white")
    pen = ImageDraw.Draw(img)
    pen.point([(190, 200), (200, 200), (210, 200)], "blue")
    pen.line([(180, 180), (220, 180), (220, 220), (180, 220), (180, 180)], "red")
    pen.rectangle((250, 250, 300, 300), "blue")
    pen.text((150, 150), text, "blue")
    img.save(outfile)

# 裁剪 Logo
crop_logo(infile, watermark)

# 绘制 Logo
draw_logo(watermark)

# 遍历 PNG 文件并添加水印
for file in Path(path).rglob('*.png'):
    name = file.stem
    outfile = os.path.join(path, f"{name}_mark.png")
    img_watermark(file, watermark, outfile)
```

## 代码分析
### 裁剪 Logo：
- crop_logo 函数从输入图像中裁剪出一个 100x100 像素的区域，并将其保存为水印。

### 添加水印：
- img_watermark 函数将裁剪出的 logo 作为水印添加到指定的图像上，放置在右下角。

### 绘制 Logo：
- draw_logo 函数创建一个新的 400x400 像素的图像，在其中绘制了一些图形和文本，并保存为 logo 图像。

### 遍历 PNG 文件：
- 使用 Path.rglob() 方法查找指定目录下的所有 PNG 文件，并对每个文件应用水印。

## 改进建议
### 路径处理：
- 使用 os.path.join() 以确保路径在不同操作系统上兼容。

### 异常处理：
- 可以在打开和保存图像时添加异常处理，以避免在文件不存在或无法写入时崩溃。

### 参数化：
- 考虑将某些参数（如裁剪区域、图像大小等）作为函数参数，以提高灵活性。

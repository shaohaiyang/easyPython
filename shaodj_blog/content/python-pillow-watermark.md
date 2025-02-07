Title: 使用 PIL(pillow) 实现图片水印*优化版
Slug: python-pillow-watermark
Date: 2025-02-07 15:55
Category: 编程
Tags: blog, python, pillow, pil

**Pillow** 是一个用于图像处理的 Python 库，是 Python Imaging Library (PIL) 的一个分支和更新版本。它提供了丰富的功能，用于打开、操作和保存多种格式的图像。

## 优点
- 易于使用：Pillow 提供了简单易懂的 API，适合初学者和专业开发者使用。

- 支持多种格式：可以处理多种图像格式，如 JPEG、PNG、GIF、BMP 等。

- 图像处理功能强大：提供了多种图像处理功能，包括图像增强、过滤、变换、裁剪、旋转等。

- 图像创建：可以方便地创建新图像，绘制文本和图形。

- 快速高效：经过优化，能够处理较大的图像文件而不会显著影响性能。

- 文档完善：Pillow 的文档详细，提供了丰富的示例，便于学习和使用。

- 社区支持：作为一个广泛使用的库，Pillow 拥有活跃的社区，可以获得各种资源和支持。

## 增加文字水印的代码
```python
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from platform import system
 
version = 0.8
 
def IsValidImage(img_path):
    """
    判断文件是否为有效（完整）的图片
    :param img_path:图片路径
    :return:True：有效 False：无效
    """
    Valid = True
    try:
        Image.open(img_path).verify()
    except:
        Valid = False
    return Valid
 
 
def add_mark_png(file, words, size=60, color=(200, 200, 200)):
    # 设置所使用的字体
    if "Darwin" in system():
        font_file = r"/System/Library/Fonts/PingFang.ttc"
    elif "Windows" in system():
        font_file = r"C:\windows\Fonts\msyh.ttc"
    font = ImageFont.truetype(font_file, int(size))
 
    # Opening Image & Creating New Text Layer
    img = Image.open(file)
    if (Path(file).suffix).lower() == ".png":
        txt = Image.new('RGBA', img.size, (255, 255, 255, 0))
    # 针对jpeg无透明通道,先创建水印图片的模式
    else:
        txt = Image.new('L', img.size)
 
    # Creating Draw Object
    d = ImageDraw.Draw(txt)
 
    # Positioning Text
    width, height = img.size
    x = y = 0
    # textwidth, textheight = d.textsize(words, font)
    # x=width/2-textwidth/2
    # y=height-textheight-300
 
    while y < height or x < width:
        mark = txt.rotate(16.8)
        if (Path(file).suffix).lower() == ".png":
            d.text((x, y), words, fill=(255, 255, 255, 155), font=font)
        else:
            d.text((x, y), words, fill=100, font=font)
        x += 50
        y += 120
 
    # 另存图片
    dir_name = Path(file).parent.joinpath("水印图")
    if not dir_name.is_dir():
        Path.mkdir(dir_name)
    file_name = (Path(file).stem + "_new" + Path(file).suffix.lower()).replace(" ", "_")
    file_name = dir_name.joinpath(file_name)
 
    if (Path(file).suffix).lower() == ".png":
        try:
            watermarked = Image.alpha_composite(img, mark)
            watermarked.save(file_name)
        except:
            rgb_im = img.convert('RGB')
            rgb_im.paste(color, (0, 0), mark)
            rgb_im.save(file_name)
    else:  # 针对jpeg格式的图片,用paste方法
        img.paste(color, (0, 0), mark)
        img.save(file_name)
```


## 图片转pdf的代码
- 打开图像：使用 Image.open() 打开指定路径的图像文件。

- 模式检查与转换：如果图像不是 RGB 模式，则将其转换为 RGB 模式。PDF 格式通常要求图像为 RGB。

- 保存为 PDF：使用 image.save() 方法将图像保存为 PDF 文件，同时可以指定分辨率。

- 支持多图像：如果需要支持将多个图像合并为一个 PDF，可以使用 save() 方法的 append_images 参数。

```python
from PIL import Image

def image_to_pdf(image_path, pdf_path):
    # 打开图像文件
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    # 检查图像模式，如果不是 RGB，则转换为 RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    # 保存图像为 PDF 文件
    image.save(pdf_path, "PDF", resolution=100.0)
```
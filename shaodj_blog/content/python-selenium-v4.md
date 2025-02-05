Title: 使用 Selenium & webdriver 自动化测试
Slug: python-selenium-web
Date: 2025-02-04 14:08
Category: 编程
Tags: blog, python

**Selenium** 是 Python 生态中最强大的工具之一，特别适合处理动态网页和复杂用户交互场景。无论是用于自动化测试、数据抓取、还是 Web 爬虫、任务自动化（如表单提交、网页截图、数据抓取等），`Selenium` 都是一个优秀的选择。

## Selenium 的一些优秀特性和用途：

---

## 1. 跨浏览器支持

Selenium 支持多种浏览器，包括：

- **Chrome**（通过 ChromeDriver）

- **Edge**（通过 EdgeDriver）

- **Firefox**（通过 GeckoDriver）

- **Safari**（通过 SafariDriver）

- **Opera** 等。

这使得 Selenium 可以在不同的浏览器环境中运行相同的脚本，确保兼容性。

## 2. 支持多种编程语言
Selenium 不仅支持 Python，还支持：

- Java

- JavaScript (Node.js)

- C#

- Ruby

- PHP 等。

这使得开发者可以使用自己熟悉的语言来编写自动化脚本。

## 3. 强大的元素定位功能
Selenium 提供了多种定位网页元素的方式，例如：

- **By ID**: `find_element(By.ID, "element_id")`

- **By Class Name**: `find_element(By.CLASS_NAME, "class_name")`

- **By Name**: `find_element(By.NAME, "name")`

- **By Tag Name**: `find_element(By.TAG_NAME, "tag_name")`

- **By CSS Selector**: `find_element(By.CSS_SELECTOR, "css_selector")`

- **By XPath**: `find_element(By.XPATH, "xpath_expression")`

这些定位方式使得 Selenium 可以灵活地与网页中的任何元素交互。

## 4. 丰富的操作功能
Selenium 不仅可以点击按钮、输入文本，还可以：

- 提交表单
- 处理下拉菜单
- 上传文件
- 执行 JavaScript 代码
- 截图
- 处理弹窗（如警告框、确认框）
- 切换窗口或 iframe

这些功能使得 Selenium 可以模拟几乎所有的用户操作。

## 5. 支持动态网页
Selenium 可以处理 JavaScript 动态加载的内容，这是它与传统爬虫工具（如 `requests` 库）相比的最大优势。它能够等待页面完全加载后再进行操作，甚至可以与动态生成的元素交互。

## 6. 支持无头模式（Headless Mode）
通过启用无头模式（如 `options.add_argument('headless')`），Selenium 可以在后台运行浏览器，无需打开 GUI 界面。这对于服务器环境或自动化任务非常有用，可以节省资源并提高效率。

## 7. 强大的等待机制
Selenium 提供了两种等待机制来处理异步加载的内容：

- **隐式等待（Implicit Wait）**：全局等待时间，适用于所有元素。
```python
driver.implicitly_wait(10)  # 等待最多 10 秒
```

- **显式等待（Explicit Wait）**：针对特定条件等待，直到条件满足或超时。
```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "element_id"))
)
```

## 8. 支持分布式测试
通过 Selenium Grid，可以在多台机器上并行运行测试脚本，显著提高测试效率。

## 9. 社区支持和文档丰富
Selenium 拥有庞大的用户社区和丰富的文档资源，遇到问题时可以轻松找到解决方案。

## 10. 应用场景广泛
Selenium 不仅用于测试，还可以用于：

- Web 爬虫：抓取动态加载的数据。

- 自动化任务：如自动填写表单、自动登录、自动下载文件等。

- 网页监控：定期检查网页内容变化。

- 性能测试：模拟用户操作，测试网页性能。

## 11. 与其他工具集成
Selenium 可以与其他工具和框架集成，例如：

- Pytest：用于编写更结构化的测试脚本。

- BeautifulSoup：用于解析抓取的网页内容。

- Pandas：用于处理和分析抓取的数据。

- Docker：用于在容器化环境中运行 Selenium。

## 12. 开源和免费
Selenium 是一个开源项目，完全免费使用，适合个人和企业。

---

# 使用Selenium v4 编写脚本
## 预约球场
```python
import datetime, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 设置 Edge 选项
options = Options()
options.use_chromium = True  # This is required for Selenium 4
options.add_argument('headless')  # 运行无界面模式
options.add_argument('--disable-gpu')  # 可选：禁用 GPU 硬件加速
options.add_argument('--window-size=1920,1080')  # 可选：设置窗口大小

# 初始化 WebDriver 服务
service = Service(executable_path=r'C:\chromedriver.exe')

try:
    driver = webdriver.Edge(service=service, options=options)
    
    for day in range(1, days + 1):
        daytime = (datetime.date.today() + datetime.timedelta(days=day)).timetuple()
        daytime = int(time.mktime(daytime))
        url = f"https://xihuwenti.juyancn.cn/wechat/product/details?id=753&time={daytime}"
        
        driver.get(url)

        # 等待元素加载
        elems = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'can-select'))
        )
        
        for elem in elems:
            start_time = elem.get_attribute('data-start')
            end_time = elem.get_attribute('data-end')
            if start_time == "12:00" or end_time == "18:00":
                hall_name = elem.get_attribute('data-hall_name')
                print(day, hall_name, start_time, end_time)

except Exception as e:
  raise(e)
 
finally:
  driver.quit()
```
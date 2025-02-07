Title: 使用 Pandas 实现基本的数据分析
Slug: python-pandas
Date: 2025-02-02 10:16
Category: 编程
Tags: blog, python, pandas, excel, xls, xlsx

**Pandas** 一个强大的分析结构化数据的工具集，基础是 [Numpy](https://www.runoob.com/numpy/numpy-tutorial.html)（提供高性能的矩阵运算）。

## 数据结构
Pandas 的主要数据结构是 Series （一维数据）与 DataFrame（二维数据）。

- Series 是一种类似于一维数组的对象，它由一组数据（各种 Numpy 数据类型）以及一组与之相关的数据标签（即索引）组成。
![serier](/images/pandas-series.png)

- DataFrame 是一个表格型的数据结构，它含有一组有序的列，每列可以是不同的值类型（数值、字符串、布尔型值）。DataFrame 既有行索引也有列索引，它可以被看做由 Series 组成的字典（共同用一个索引）。
![dataframe](/images/pandas-dataframe.png)
![dataframe](/images/pandas-df2.png)

## Pandas 应用
- Pandas 可以从各种文件格式比如 CSV、JSON、SQL、Microsoft Excel 导入数据。

- Pandas 可以对各种数据进行运算操作，比如归并、再成形、选择，还有数据清洗和数据加工特征。

- Pandas 广泛应用在学术、金融、统计学等各个数据分析领域。

## Pandas 功能
Pandas 是数据分析的利器，它不仅提供了高效、灵活的数据结构，还能帮助你以极低的成本完成复杂的数据操作和分析任务。

Pandas 提供了丰富的功能，包括：

- 数据清洗：处理缺失数据、重复数据等。

- 数据转换：改变数据的形状、结构或格式。

- 数据分析：进行统计分析、聚合、分组等。

- 数据可视化：通过整合 Matplotlib 和 Seaborn 等库，可以进行数据可视化。


**Pandas 是 Python** 数据科学领域中不可或缺的工具之一，它的灵活性和强大的功能使得数据处理和分析变得更加简单和高效。

可运行的代码实例
```python
import pandas as pd
import matplotlib.pyplot as plt

# 中文支持，不会显示小方框
plt.rcParams['font.sans-serif'] = ['SimHei', 'Songti SC', 'STFangsong']
# 正常显示负号
plt.rcParams['axes.unicode_minus'] = False
# 设置线条宽度
plt.rcParams['lines.linewidth'] = 50
# 设置线条颜色
plt.rcParams['lines.color'] = 'red'
# 设置线条样式，样式的各类还有 `--`为虚线，`-.`为点虚线
plt.rcParams['lines.linestyle'] = '--' # 直线

# 1. 创建一个示例 DataFrame
data = {
    'Name': ['张三', '李四', '王五', '赵六', '田七'],
    'Age': [24, 27, 22, 32, 29],
    'Salary': [5000, 8500, 6800, 7200, 6500],
    'Department': ['HR', 'IT', 'Finance', 'IT', 'HR']
}
 
df = pd.DataFrame(data)
 
# 2. 数据查看
print(f"DataFrame: \n{df} \n")
 
# 3. 基本统计
print(f"基本统计: \n {df.describe()} \n")
 
# 4. 数据选择
print(f"选择 'Name' 和 'Salary' 列: \n {df[ ['Name', 'Salary']]} \n")
 
# 5. 添加新列
df['Bonus'] = df['Salary'] * 0.1
print(f"添加 'Bonus' 列: \n {df} \n")
 
# 6. 条件筛选
print(f"筛选出薪水大于 6000 的员工: \n {df[df['Salary'] > 6000]} \n")
 
# 7. 分组统计
grouped = df.groupby('Department').mean(numeric_only=True)  # 只计算数值列
print(f"按部门分组的平均值: \n {grouped} \n")
 
# 8. 处理缺失值
df.loc[1, 'Salary'] = None  # 人为制造缺失值
print(f"处理缺失值: \n {df.fillna( df['Salary'].mean())} \n")
 
# 9. 数据排序
print(f"按年龄排序: \n {df.sort_values(by='Age')}")

# 10. 数据可视化
plt.figure(figsize=(10, 5))
plt.xlabel('姓名')
plt.ylabel('薪资')
plt.title('员工薪水')
plt.bar(df['Name'], df['Salary'], color='blue')
plt.show()
```
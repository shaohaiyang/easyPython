# 好运背古诗
import random, os, time

def readAllWithLine(filePath):
  result = []
  with open(filePath, encoding="UTF-8") as f:
    for line in f.readlines():
      result.append(line)
  return result

def formateLine(s):
  slice = s.split(":")
  if len(slice) < 2:
    raise TypeError("无效的一行数据")
  return (slice[0], slice[1].replace("\n", ""))

def loadData():
  result = dict()
  filePath = os.path.abspath(os.path.join(__file__, os.path.pardir,  "data.txt"))
  for s in readAllWithLine(filePath):
    (key, value) = formateLine(s)
    result.setdefault(key, value)
  return result

if __name__ == "__main__":
  gushi = loadData()
  gushi_list = random.sample(gushi.keys(), 15)
  for key1 in gushi_list:
    print(f"{key1} ->  {gushi.get(key1)}...")

import os
import turtle as tt
import random

cur_path = os.getcwd()
with open(cur_path+"/gushi.txt","r",encoding='utf8') as f:
    words = []
    for line in f:
        line = line.strip() # 去除空白符号和换行符
        if '、' in line:
            words += [ word for word in line.split("、") if word.strip()]
words = set(words)
print(len(words))

num = int(tt.numinput("挑战一下吧(空格开始)", "请输入要挑战的成语数量：",80,30,100))
hidden = int(tt.numinput("难度等级(空格开始)", "请输入要挑战难度：",1,1,3))

size = int(num/2.3)
w = size * num / 3 + 200
h = w + 50
win = tt.Screen()
win.bgcolor("black")
win.setup(w, h)
win.title("成语大冒险 [按空格键开始]")
pen = tt.Pen(shape="turtle")
pen.speed(0)
pen.pensize(1)
pen.up()
pen.ht()
color = ["red","yellow","white","orange","pink"]

def pp():
    pen.clear()
    y = h/2 - size*2
    x = -w/2 + size*2
    x1 = 1
    y1 = 1
    for word in random.sample(words,num):
        word = list(word)
        for _ in range(hidden):
            pos = random.randint(0,3)
            word[pos] = "?"
        word = ''.join(word)
        pen.goto(x,y)
        pen.color(random.choice(color))
        print(word,x1,y1)
        pen.write(word,font=("宋体",size,'normal'))
        if pen.xcor() < w/2 - size*8:
            x += size * 6
        else:
            x = -w/2 + size*2
            y -= size*2
            y1 += 1
        x1 += 1

def getPos(x,y):
    print("(", x, "," ,y,")")
    if -100 < x < 100 and -100 < y < 100:
        tt.textinput('正确答案:', '鸡飞狗跳')

print(w,h/2)
#tt.onkey(pp,"space")
tt.listen()
win.onclick(getPos)
tt.done()

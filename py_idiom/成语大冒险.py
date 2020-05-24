with open("gushi.txt","r") as f:
    words = []
    for line in f:
        line = line.strip() # 去除空白符号和换行符
        if '、' in line:
            words += [ word for word in line.split("、") if word.strip()]
 
import turtle as tt
import random
size = 35
num = int(tt.numinput("挑战一下吧", "请输入要挑战的成语数量：",60,30,100))
hidden = int(tt.numinput("难度等级", "请输入要挑战难度：",1,1,3))
 
w = size * num / 3 + 200
h = w + 250
win = tt.Screen()
win.bgcolor("black")
win.setup(w, h)
win.title("成语大冒险")
pen = tt.Pen(shape="turtle")
pen.speed(0)
pen.pensize(1)
pen.up()
pen.ht()
color = ["red","yellow","orange","pink"]

def pp():
    pen.clear()
    y = h/2 - size*2
    x = -w/2 + size*2
    
    for word in random.sample(words,num):
        word = list(word)
        for _ in range(hidden):
            pos = random.randint(0,3)
            word[pos] = " * "
        word = ''.join(word)
        pen.goto(x,y)
        pen.color(random.choice(color))
        pen.write(word,font=("楷体",size,'normal'))
        if pen.xcor() < w/2 - size*8:
            x += size * 6
        else:
            x = -w/2 + size*2
            y -= size*2

tt.onkey(pp,"space")
tt.listen()
tt.done()
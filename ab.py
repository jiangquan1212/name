from datetime import datetime
def f():
    now=datetime.now()
    a=now.strftime("%Y年%m月%d日 %H:%M:%S")
    b=now.strftime("%A,%B,%d,%Y")
    return a,b
import string
import random
def k():
    a = string.digits + string.ascii_uppercase
    b=(''.join([random.choice(a) for j in range(0, 6)]))
    return b


from datetime import datetime
def o():
    now=datetime.now()
    t=now.strftime("%Y年%m月%d日 %H:%M:%S")
    return t
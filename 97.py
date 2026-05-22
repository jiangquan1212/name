#a=input('输入字母')
#b=input('输入字母')
#c=input('输入字母')
#lst=[a,b,c]
#lst.sort()
#print(lst)
from fontTools.misc.cython import returns

#a=input('输入字母')
#b=input('输入字母')
#c=input('输入字母')
#if a>b:
    #a,b=b,a
#if a>c:
    #a,c=c,a
#if b>c:
    #b,c=c,b
#print(a,b,c)





#print(ord('A'))
#a=input()
#for i in a:
    #if 123>ord(i)>96 :
        #print(chr(ord(i)-32),end='')
    #elif 92>ord(i)>64:
        #print(chr(ord(i) + 32),end='')
    #else:
        #print("输入不合法")

while True:
    a=float(input('输入第一个数'))
    b=float(input('输入第二个输'))
    c=input("输入+,-,*,/中的一个")
    if c=='/' and b!=0:
        print(a/b)
    elif c=='+':
        print(a+b)
    elif c=='-':
        print(a-b)
    elif c=='*':
        print(a*b)
    elif c=='/' and b==0:
        print("被除数不能为0")

    d=input('输入yes或者是no')
    if d=='yes':
        continue
    elif d=='no':
        break
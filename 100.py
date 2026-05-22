#b=input('输入水果名称')
#a=['苹果','香蕉','葡萄','梨']
#if b in a:
    #c=a.index(b)
    #print(c+1)
#else:
    #print('没有这个水果')


#a=list(map(str,range(6)))
#for i in a:
    #print(int(i)**2,end=' ')


#a=list(range(1,10))
#def f(i):
       #return i%2==0
#filter(f,a)
#c=list(filter(f,a))
#print(c)


#1,-2,3,-4,5,-6
#a=list(map(int,input('输入数字用空格分开').split()))
#def f(x):
    #return x>0
#b=list(filter(f,a))
#c=map(lambda x: x * 2, b)
#for i in c:
    #print(i,end=' ')

#a=list(zip('abcd',[34,57,87,98]))
#b=0
#for i,j in a:
    #if j>60:
        #b+=1
        #print('合格的是:',i,'成绩是:',j)
#print('及格的人数为：',b)

#n=int(input('输入学生人数:'))
#for k in range(0,n):
    #x=input('输入学生姓名:')
    #y=input('输入学科名称:').split()
    #z=map(int,input('输入学生成绩').split())
    #a=list(zip(y,z))
    #c=len(a)
    #d=0
    #for i,j in a:
        #b=b+j
    #d=b/c
    #print(x,'总分为：',b)
    #print(x,f'平均分为：{d:.2f}',)
    #if d>85:
        #print('学生成绩优秀')
    #elif d<60:
        #print('学生成绩不及格')
    #else:
        #print('学生成绩合格')



n=int(input('输入学生人数:'))
t={}
for m in range(0,n):
    x=input('输入学生姓名:')
    y=input('输入学科名称:').split()
    z=map(int,input('输入学生成绩').split())
    a=list(zip(y,z))
    for h,k in a:
        if h not in t:
            t[h]=(k,x)
        elif k>t[h][0]:
            t[h]=(k,x)
    b=0
    c=len(a)
    d=0
    for i,j in a:
        b=b+j
    d=b/c
    print(x,'总分为：',b)
    print(x,f'平均分为：{d:.2f}',)
    if d>85:
        print('学生成绩优秀')
    elif d<60:
        print('学生成绩不及格')
    else:
        print('学生成绩合格')
    print()
for h, (i, name) in t.items():
    print(f'{h}最高分: {i}分（{name}）')




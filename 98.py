#a=input()
#b=list(a)
#c=len(b)
#d=0
#for i in range(c,-1,-1):
    #d=d+i*10**(i-1)
#print(f'数是:{d:.0f}')


#while True:
    #i=int(input('输入成绩'))
    #if 100>i>=90:
        #print('该学生成绩评为A')
    #elif 90>i>=80:
        #print('该学生成绩评为B')
    #elif 80>i>=70:
        #print('该学生成绩评为C')
    #elif 70>i>=60:
        #print('该学生成绩评为D')
    #elif 60>i>=0:
        #print('该学生成绩不及格')
    #else:
        #print('输入错误,请输入0-100的数')
    #b=input('是否继续,输入yes或者是no')
    #if b=='no':
        #break
#while True:
    #n=int(input('输入多少个分数'))
    #if n>=0:
        #b=0
        #for i in range(n):
            #a=int(input())
            #if a>=0:
               #b=b+a
               #c=b/(i+1)
               #print(f'平均分数是:{c:.2f}')
            #else:
                #print('输入大于0的数')
        #d = input('是否继续输入分数yes或者是no')
        #if d=='no':
           # break
    #else:
       # print('输入大于0的数')


#def f(a):
    #if a < 2:
        #return False
    #for i in range(2, int(a ** 0.5) + 1):
        #if a % i == 0:
            #return False
    #return True

#c = 0
#for a in range(2, 101):
    #if f(a):
        #c += a
       # print(f'{a}是素数')

#print(f'素数和为：{c}')

#def f(a):
        #if a%7==0 and a%5!=0:
            #return True
        #else:
            #return False

#c = 0
#for a in range(1, 101):
    #if f(a):
        #c += a
        #print(a)

#print(f'和为：{c}')



#for i in range(100,1000):
    #a=i//100
    #b=(i//10)%10
    #c=i%10
    #if a**3+b**3+c**3==i:
        #print(i)



#n=int(input())
#for i in range(10**(n-1),10**n):
    #a=str(i)
    #b=0
    #for j in a:
        #b+=int(j)**n
    #if i==b:
        #print(i)


a=list(input())
print(a)
a.append(5)
print(a)
b=list(input())
a.extend(b)
print(a)
a.insert(3,11)
print(a)
a.remove(5)
print(a)
a.pop(1)
print(a)
print(a.count(5))
a.clear()
print(a)
a.sort()
print(a)
a.reverse()
print(a)

c=[1,2,3,4]
print(c[1])
c[1:3]=[88,99]
print(c)
c[1]=75
print(c)

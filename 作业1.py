class Bankaccount:
    def __init__(self, account, name, balance, password):
        self.account = account
        self.name = name
        self.__balance = balance
        self.__password = password
    def show_balance(self, a):
        if a == self.__password:
            print(f"余额是{self.__balance}元")
        else:
            print("密码错误,拒绝访问")
    def deposit(self, b):
        if b > 0:
            self.__balance = self.__balance + b
            print(f"存入{b}元，当前余额{self.__balance}元")
        else:
            print("存入的金额必须大于0")
    def withdraw(self, c):
        if c <= self.__balance:
            self.__balance = self.__balance - c
            print(f"成功取出{c}元，当前余额{self.__balance}元")
        else:
            print("余额不足")
    def change_password(self, old, new):
        if old == self.__password:
            self.__password = new
            print("密码修改成功")
        else:
            print("密码错误，拒绝访问")
    def calculate_interest(self, pwd, years=1):
        """计算利息，年利率1.5%"""
        if pwd != self.__password:
            print("密码错误，拒绝访问")
            return
        rate = 0.015
        interest = self.__balance * rate * years
        print(f"当前余额：{self.__balance}元")
        print(f"年利率：{rate * 100}%")
        print(f"存期：{years}年")
        print(f"利息：{interest:.2f}元")
        print(f"本息合计：{self.__balance + interest:.2f}元")
print("01:开户")
print("02:查询余额")
print("03:存款操作")
print("04:取款操作")
print("05:修改密码")
print("06:计算利息")
print("07:退出系统")
q = input("输入1-7选择需要办理的业务")
if q == '1':
    account = input("输入账号:")
    name = input("输入姓名:")
    balance = float(input("输入余额:"))
    password = input("输入密码:")
    user= Bankaccount(account, name, balance, password)
elif q == '2':
    if 'user' in locals():
        a = input("输入密码:")
        user.show_balance(a)
    else:
        print("请先开户")
elif q == '3':
    if 'user' in locals():
        b = float(input("输入存款金额:"))
        user.deposit(b)
    else:
        print("请先开户")
elif q == '4':
    if 'user' in locals():
        c = float(input("输入要取出的金额:"))
        user.withdraw(c)
    else:
        print("请先开户")
elif q == '5':
    if 'user' in locals():
        old = input("输入旧密码:")
        new = input("输入新密码:")
        user.change_password(old, new)
    else:
        print("请先开户")
elif q == '6':
    if 'user' in locals():
        pwd = input("输入密码:")
        years = float(input("输入存款年限(年):"))
        user.calculate_interest(pwd, years)
    else:
        print("请先开户")
elif q == '7':
    print("退出系统")
else:
    print("请输入1-7的数字")







class Book:
    def __init__(self, title, author, price):
        self.title = title
        self.author = author
        self.price = price
    def show_info(self):
        print(f"书名：《{self.title}》")
        print(f"作者：{self.author}")
        print(f"价格：{self.price}元")
book1 = Book("三国演义", "罗贯中", 68.00)
book1.show_info()


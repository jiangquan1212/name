# main.py
#import my_calc
#print('3+5=',my_calc.add(3, 5))
#print('4x6=', my_calc.multiply(4, 6))
#print('圆周率近似值=',my_calc. PI)


#from my_calc import add
#from my_calc import multiply
#from my_calc import PI
#print('3+5=',add(3, 5))
#print('4x6=', multiply(4, 6))
#print('圆周率近似值=',PI)

#import my_calc as ab
#print('3+5=',ab.add(3, 5))
#print('4x6=',ab.multiply(4, 6))
#print('圆周率近似值=',ab. PI)

#from ab import o
#m=o()
#print(m)



#from ab import k
#l=k()
#print(l)

#import json
#user_data={"name":"李四","age":30,"skills":["Python","Java"]}
#json_str=json.dumps(user_data,ensure_ascii=True,indent=2)
#print("转换后的JSON字符串:\n",json_str)
#parsed_dict=json.loads(json_str)
#print("\n提取姓名:",parsed_dict["name"])
#print("提取技能列表:",parsed_dict["skills"])


#import json
#data={"name":"张三","age":20}
#json_str=json.dumps(data,ensure_ascii=False,indent=4)
#print(json_str)

#import json
#data={"name":"张三","age":20}
#abc=json.dumps(data,ensure_ascii=True,indent=4)
#print(abc)
#import json

#a='''{
#"company": "Alibaba",
#"employees": [{"name": "Alice", "position": "Engineer", "salary": 10000},
              #{"name": "Bob", "position": "Manager", "salary": 15000}],
#"location": "Hangzhou"}'''

#data=json.loads(a)
#print('公司名称:',data["company"])
#print('公司地址:',data["location"])
#sum=0
#c=len(data['employees'])
##print(f'姓名:{i["name"]},职位:{i["position"]}')
    #sum=sum+float(str(i['salary']))
#print(sum)
#print(sum/c)
#import pymysql
#print(pymysql.__version__)
#import pymysql
#conn=pymysql.connect(
   # host='localhost',user='root',
   # password='xw384594',db='money'
#)
#print('连接成功')
#conn.close()

#import pymysql
#try:
    #conn=pymysql.connect()
    #print('连接成功')
#except pymysql.MySQLError as c:
    #print(f"Error:{c}")

#import pymysql
#try:
    #conn=pymysql.connect(host='localhost',user='root',db='money')
    #cursor=conn.cursor()
    #cursor.execute("SELECT*from students")
    #res=cursor.fetchall()
#except pymysql.MySQLError as e:
    #print(e)
#finally:
    #cursor.close();conn.close()
#import pymysql
#conn=pymysql.connect(host='localhost',user='root',db='money',password='xw384594')
#cursor=conn.cursor()
#cursor.execute('select * from employees where 8000<=salary and salary<=10000')
#a=cursor.fetchall()
#for i in a:
    #print(i)
#cursor.close()
#conn.close()

#import pymysql
#conn=pymysql.connect(host='localhost',user='root',db='money',password='xw384594')
#cursor=conn.cursor()
#sql="insert into students(id,name,c_id)values(5,'赵六',22)"
#cursor.execute(sql)
#conn.commit()
#print(f"插入成功，影响行数:{cursor.rowcount}")

#import pymysql
#conn=pymysql.connect(host='localhost',user='root',db='money',password='xw384594')
#cursor=conn.cursor()
#students=[(6,'小明',35),(7,'小王',76)]
#sql="insert into students(id,name,c_id)values(%s,%s,%s)"
#cursor.executemany(sql,students)
#conn.commit()
#print(f"插入成功，影响行数:{cursor.rowcount}")
#import pymysql
#conn=pymysql.connect(host='localhost',user='root',db='money',password='xw384594')
#cursor=conn.cursor()
#sql="insert into employees(emp_id,emp_name,salary,dept_id)values(10,'钱九',18000,23)"
#cursor.execute(sql)
#conn.commit()
#print(f"插入成功，影响行数:{cursor.rowcount}")

#import pymysql
#conn=pymysql.connect(host='localhost',user='root',db='money',password='xw384594')
#cursor=conn.cursor()
#sql="update employees set salary=%s where emp_name=%s"
#params=(20000,"张三")
#cursor.execute(sql,params)
#conn.commit()
#print(f"插入成功，影响行数:{cursor.rowcount}")
#cursor.close()
#conn.close()
#import pymysql
#conn=pymysql.connect(host='localhost',user='root',db='money',password='xw384594')
#cursor=conn.cursor()
#sql="delete from employees where emp_name=%s"
#params = ("钱九",)
#cursor.execute(sql, params)
#conn.commit()
#cursor.close()
#cursor.close()
# UserManager.py
import pymysql
def f():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='xw384594',
        database='money'
    )
def k(sql, params=None):
    conn = f()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params or ())
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
def m(sql, params=None):
    conn = f()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params or ())
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
class UserManager:
    def __init__(self, db_helper):
        self.db = db_helper
    def ab(self, username, password, phone, gender):
        sql = "insert into user (username, password, phone, gender) values (%s, %s, %s, %s)"
        params = (username, password, phone, gender)
        return self.db.execute_update(sql, params)
    def ac(self, user_id):
        sql = "select * from user where id = %s"
        params = (user_id,)
        result = self.db.execute_query(sql, params)
        return result[0] if result else None
    def ad(self, user_id, new_phone):
        sql = "update user set phone = %s where id = %s"
        params = (new_phone, user_id)
        return self.db.execute_update(sql, params)
    def ae(self, user_id):
        sql = "delete from user where id = %s"
        params = (user_id,)
        return self.db.execute_update(sql, params)
if __name__ == "__main__":
    class DBHelper:
        def execute_update(self, sql, params=None):
            return k(sql, params)
        def execute_query(self, sql, params=None):
            return m(sql, params)
    db_helper = DBHelper()
    user_mgr = UserManager(db_helper)
    user_mgr.ab("张三", "123456", "13800138001", "男")
    user = user_mgr.ac(1)
    print("查询结果：", user)
    user_mgr.ad(1, "13900000000")
    user_mgr.ae(1)
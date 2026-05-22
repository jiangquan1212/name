import pymysql
import datetime
def write_log(x, y):
    with open("log.txt", "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] 操作人: {x} | 操作: {y}\n")
class BookManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None
        self.current_admin = None
    def g(self):
        try:
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset="utf8mb4"
            )
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False
    def k(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    def h(self):
        if not self.g():
            return False
        try:
            username = input("请输入管理员账号: ").strip()
            password = input("请输入密码: ").strip()
            sql = "select * from admin where username=%s and password=%s"
            self.cursor.execute(sql, (username, password))
            result = self.cursor.fetchone()
            if result:
                self.current_admin = username
                print(f"登录成功，欢迎 {username}！")
                write_log(username, "登录系统")
                return True
            else:
                print("账号或密码错误")
                return False
        except Exception as e:
            print(f"登录异常: {e}")
            return False
        finally:
            self.k()
    def j(self):
        try:
            book_id = input("请输入图书编号: ").strip()
            title = input("请输入书名: ").strip()
            author = input("请输入作者: ").strip()
            category = input("请输入分类: ").strip()
            if not all([book_id, title, author, category]):
                print("所有字段都不能为空")
                return
            self.g()
            self.cursor.execute("select * from book where book_id=%s", (book_id,))
            if self.cursor.fetchone():
                print("图书编号已存在")
                return
            sql = "insert into book(book_id,title,author,category,status) values(%s,%s,%s,%s,'可借阅')"
            self.cursor.execute(sql, (book_id, title, author, category))
            self.conn.commit()
            print("添加图书成功")
            write_log(self.current_admin, f"添加图书: {book_id} - {title}")
        except Exception as e:
            print(f"添加失败: {e}")
            self.conn.rollback()
        finally:
            self.k()
    def aa(self):
        self.g()
        try:
            self.cursor.execute("select book_id, title, author, category, status from book")
            books = self.cursor.fetchall()
            if not books:
                print("暂无图书数据")
                return
            print("\n" + "=" * 80)
            print(f"{'编号':<12} {'书名':<20} {'作者':<12} {'分类':<12} {'状态':<10}")
            print("-" * 80)
            for b in books:
                print(f"{b[0]:<12} {b[1]:<20} {b[2]:<12} {b[3]:<12} {b[4]:<10}")
            print("=" * 80)
            write_log(self.current_admin, "查询所有图书")
        except Exception as e:
            print(f"查询失败: {e}")
        finally:
            self.k()
    def ab(self):
        book_id = input("请输入要查询的图书编号: ").strip()
        self.g()
        try:
            self.cursor.execute("select * from book where book_id=%s", (book_id,))
            book = self.cursor.fetchone()
            if book:
                print(f"\n图书详情: 编号={book[1]}, 书名={book[2]}, 作者={book[3]}, 分类={book[4]}, 状态={book[5]}")
            else:
                print("未找到该图书")
            write_log(self.current_admin, f"按编号查询图书: {book_id}")
        except Exception as e:
            print(f"查询失败: {e}")
        finally:
            self.k()
    def ac(self):
        book_id = input("请输入要修改的图书编号: ").strip()
        self.g()
        try:
            self.cursor.execute("select * from book where book_id=%s", (book_id,))
            if not self.cursor.fetchone():
                print("图书不存在")
                return
            new_title = input("请输入新书名（直接回车保留原值）: ").strip()
            new_author = input("请输入新作者（直接回车保留原值）: ").strip()
            new_category = input("请输入新分类（直接回车保留原值）: ").strip()
            updates = []
            params = []
            if new_title:
                updates.append("title=%s")
                params.append(new_title)
            if new_author:
                updates.append("author=%s")
                params.append(new_author)
            if new_category:
                updates.append("category=%s")
                params.append(new_category)
            if updates:
                sql = f"update book set {','.join(updates)} where book_id=%s"  # 修复: ser -> set
                params.append(book_id)
                self.cursor.execute(sql, params)
                self.conn.commit()
                print("修改成功")
                write_log(self.current_admin, f"修改图书信息: {book_id}")
            else:
                print("未做任何修改")
        except Exception as e:
            print(f"修改失败: {e}")
            self.conn.rollback()
        finally:
            self.k()
    def ad(self):
        book_id = input("请输入要删除的图书编号: ").strip()
        self.g()
        try:
            self.cursor.execute("select * from book where book_id=%s", (book_id,))
            if not self.cursor.fetchone():
                print("图书不存在")
                return
            confirm = input(f"确认删除图书 {book_id} 吗？(y/n): ").lower()
            if confirm != 'y':
                print("已取消删除")
                return
            self.cursor.execute("delete from book where book_id=%s", (book_id,))
            self.conn.commit()
            print("删除成功")
            write_log(self.current_admin, f"删除图书: {book_id}")
        except Exception as e:
            print(f"删除失败: {e}")
            self.conn.rollback()
        finally:
            self.k()
    def ae(self):
        book_id = input("请输入要借阅的图书编号: ").strip()
        self.g()
        try:
            self.cursor.execute("select status from book where book_id=%s", (book_id,))
            res = self.cursor.fetchone()
            if not res:
                print("图书不存在")
                return
            if res[0] == "已借出":
                print("图书已被借出")
                return
            self.cursor.execute("update book set status='已借出' where book_id=%s", (book_id,))
            self.conn.commit()
            print("借阅成功")
            write_log(self.current_admin, f"借阅图书: {book_id}")
        except Exception as e:
            print(f"借阅失败: {e}")
            self.conn.rollback()
        finally:
            self.k()
    def af(self):
        book_id = input("请输入要归还的图书编号: ").strip()
        self.g()
        try:
            self.cursor.execute("select status from book where book_id=%s", (book_id,))
            res = self.cursor.fetchone()
            if not res:
                print("图书不存在")
                return
            if res[0] == "可借阅":
                print("图书未被借出")
                return
            self.cursor.execute("update book set status='可借阅' where book_id=%s", (book_id,))
            self.conn.commit()
            print("归还成功")
            write_log(self.current_admin, f"归还图书: {book_id}")
        except Exception as e:
            print(f"归还失败: {e}")
            self.conn.rollback()
        finally:
            self.k()
    def ag(self):
        if not self.h():
            return
        while True:
            print("        图书借阅管理系统")
            print("1. 添加图书")
            print("2. 查询所有图书")
            print("3. 按编号查询图书")
            print("4. 修改图书信息")
            print("5. 删除图书")
            print("6. 借阅图书")
            print("7. 归还图书")
            print("0. 退出系统")
            choice = input("请选择操作: ").strip()
            if choice == "1":
                self.j()
            elif choice == "2":
                self.aa()
            elif choice == "3":
                self.ab()
            elif choice == "4":
                self.ac()
            elif choice == "5":
                self.ad()
            elif choice == "6":
                self.ae()
            elif choice == "7":
                self.af()
            elif choice == "0":
                print("感谢使用，再见！")
                write_log(self.current_admin, "退出系统")
                break
            else:
                print("无效输入，请输入 0-7 之间的数字")
if __name__ == "__main__":
    manager = BookManager(
        host="localhost",
        user="root",
        password="xw384594",
        database="book_db"
    )
    manager.ag()
import psycopg2

# 配置数据库连接
hostname = "localhost"
port = "5432"
dbname = "mydb"  # 确保数据库已经存在
user = "postgres"  # PostgreSQL 默认的超级用户
password = "123456"  # 替换为您的数据库密码


# 连接到数据库并确保编码为 UTF-8
def connect_db():
    try:
        conn = psycopg2.connect(
            host=hostname,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            options="-c client_encoding=UTF8"  # 确保连接编码为 UTF-8
        )
        return conn
    except Exception as e:
        print(f"连接数据库失败: {e}")
        return None


# 创建学生表（如果表不存在）
def create_table(conn):
    try:
        cursor = conn.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            age INT,
            gender VARCHAR(10),
            email VARCHAR(100)
        );
        """
        cursor.execute(create_table_sql)
        conn.commit()
        print("表 'students' 已创建或已存在。")
        cursor.close()
    except Exception as e:
        print(f"创建表失败: {e}")


# 添加学生信息
def add_student(conn, name, age, gender, email):
    try:
        cursor = conn.cursor()
        insert_sql = """
        INSERT INTO students (name, age, gender, email)
        VALUES (%s, %s, %s, %s);
        """
        student_data = (name, age, gender, email)
        cursor.execute(insert_sql, student_data)
        conn.commit()
        print(f"学生 {name} 信息添加成功！")
        cursor.close()
    except Exception as e:
        print(f"添加学生信息失败: {e}")


# 查询所有学生信息
def get_all_students(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students;")
        rows = cursor.fetchall()
        print("所有学生信息：")
        for row in rows:
            print(f"学号: {row[0]}, 姓名: {row[1]}, 年龄: {row[2]}, 性别: {row[3]}, 邮箱: {row[4]}")
        cursor.close()
    except Exception as e:
        print(f"查询学生信息失败: {e}")


# 更新学生信息
def update_student(conn, student_id, name=None, age=None, gender=None, email=None):
    try:
        cursor = conn.cursor()

        # 动态构建更新语句
        update_query = "UPDATE students SET "
        values = []

        if name:
            update_query += "name = %s, "
            values.append(name)
        if age:
            update_query += "age = %s, "
            values.append(age)
        if gender:
            update_query += "gender = %s, "
            values.append(gender)
        if email:
            update_query += "email = %s, "
            values.append(email)

        # 去掉多余的逗号
        update_query = update_query.rstrip(", ") + " WHERE id = %s"
        values.append(student_id)

        cursor.execute(update_query, tuple(values))
        conn.commit()
        print(f"学号为 {student_id} 的学生信息已更新！")
        cursor.close()
    except Exception as e:
        print(f"更新学生信息失败: {e}")


# 删除学生信息
def delete_student(conn, student_id):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        conn.commit()
        print(f"学号为 {student_id} 的学生信息已删除！")
        cursor.close()
    except Exception as e:
        print(f"删除学生信息失败: {e}")


# 主程序
def main():
    conn = connect_db()

    if conn:
        # 创建学生表（如果未创建）
        create_table(conn)

        while True:
            print("\n----- 学生信息管理系统 -----")
            print("1. 添加学生")
            print("2. 查看所有学生")
            print("3. 更新学生信息")
            print("4. 删除学生")
            print("5. 退出")

            choice = input("请输入您的选择: ")

            if choice == "1":
                name = input("请输入学生姓名: ")
                age = int(input("请输入学生年龄: "))
                gender = input("请输入学生性别: ")
                email = input("请输入学生邮箱: ")
                add_student(conn, name, age, gender, email)

            elif choice == "2":
                get_all_students(conn)

            elif choice == "3":
                student_id = int(input("请输入要更新的学生学号: "))
                name = input("请输入新的姓名（留空则不更新）: ")
                age = input("请输入新的年龄（留空则不更新）: ")
                gender = input("请输入新的性别（留空则不更新）: ")
                email = input("请输入新的邮箱（留空则不更新）: ")

                if age:
                    age = int(age)
                update_student(conn, student_id, name, age, gender, email)

            elif choice == "4":
                student_id = int(input("请输入要删除的学生学号: "))
                delete_student(conn, student_id)

            elif choice == "5":
                print("感谢使用学生信息管理系统，再见！")
                break

            else:
                print("无效选择，请重新输入！")

        conn.close()


if __name__ == "__main__":
    main()

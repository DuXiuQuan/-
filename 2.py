import psycopg2
from psycopg2 import sql


# 连接数据库
def connect_db():
    try:
        connection = psycopg2.connect(
            host="pg.byr.plus",  # 数据库主机名
            port="5432",  # 数据库端口
            user="secondclass",  # 数据库用户名
            password="K4FbfHmkBfoLsE",  # 数据库密码
            dbname="secondclass"  # 数据库名
        )
        return connection
    except Exception as error:
        print("Error while connecting to database:", error)
        return None


# 根据活动规则计算积分
def calculate_points(participation, activity):
    points = 0
    demands = activity['demands']

    requires_signup = (demands & 1) > 0  # 是否需要报名
    requires_checkin = (demands & 2) > 0  # 是否需要签到

    # 如果活动需要报名
    if requires_signup:
        if participation['sign_up_time'] is not None:
            if requires_checkin:
                # 报名且签到
                if participation['checkin_time'] is not None:
                    points = 3
                else:
                    points = -3  # 报名但未签到
            else:
                points = 1  # 只需要报名
        else:
            points = 0  # 没有报名没有积分
    else:
        # 活动不需要报名，但需要签到
        if requires_checkin:
            if participation['checkin_time'] is not None:
                points = 2  # 不需要报名但签到
            else:
                points = 0  # 没有签到没有积分
        else:
            points = 0  # 不需要报名和签到

    return points


# 更新用户积分
def update_user_scores(conn, user_id, points_to_add, belong_to):
    cursor = conn.cursor()
    try:
        # 查询是否已有记录
        cursor.execute(
            sql.SQL("SELECT score FROM user_scores WHERE user_id = %s AND belong_to = %s"),
            [user_id, belong_to]
        )
        result = cursor.fetchone()
        if result:
            current_score = result[0]
            new_score = current_score + points_to_add
            cursor.execute(
                sql.SQL("UPDATE user_scores SET score = %s WHERE user_id = %s AND belong_to = %s"),
                [new_score, user_id, belong_to]
            )
        else:
            cursor.execute(
                sql.SQL("INSERT INTO user_scores (user_id, score, belong_to) VALUES (%s, %s, %s)"),
                [user_id, points_to_add, belong_to]
            )
        conn.commit()
    except Exception as error:
        print("Error updating user score:", error)
        conn.rollback()
    finally:
        cursor.close()


# 主程序
def main():
    user_id = 2024212681  # 测试用户 ID
    belong_to = 0  # 假设为校级积分，belong_to = 0

    # 连接数据库
    conn = connect_db()
    if not conn:
        return

    cursor = conn.cursor()

    try:
        # 查询该用户的所有活动参与记录
        cursor.execute("SELECT * FROM participation WHERE user_id = %s", [user_id])
        participations = cursor.fetchall()

        for participation in participations:
            act_id, sign_up_time, checkin_time = participation[1], participation[3], participation[4]

            # 获取活动信息
            cursor.execute("SELECT * FROM activities WHERE id = %s", [act_id])
            activity = cursor.fetchone()

            # 如果活动类型符合条件，计算积分
            if activity:
                # 将活动信息转换为字典
                activity_dict = {
                    'id': activity[0],
                    'name': activity[1],
                    'demands': activity[12],  # demands 是第 13 列
                }

                # 计算该活动的积分
                points = calculate_points(participation, activity_dict)

                # 更新该学生的积分
                update_user_scores(conn, user_id, points, belong_to)
                print(f"User {user_id} earned {points} points for activity {activity_dict['name']}.")
    except Exception as error:
        print("Error processing data:", error)
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()

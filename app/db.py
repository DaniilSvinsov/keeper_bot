import sqlite3


class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверяем, есть ли юзер в базе"""
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_info(self, user_id):
        """Достаем id юзера в базе по его user_id"""
        result = self.cursor.execute("SELECT `user_id`, `join_date`, `user_name` FROM `users` WHERE `user_id` = ?",
                                     (user_id,))
        return result.fetchall()

    def add_user(self, user_id, user_name):
        """Добавляем юзера в базу"""
        self.cursor.execute("INSERT INTO `users` (`user_id`, `user_name`) VALUES (?, ?)", (user_id, user_name))
        return self.conn.commit()

    def add_record(self, user_id, operation, amount, category):
        """Создаем запись о доходах/расходах"""
        self.cursor.execute("INSERT INTO `records` (`users_id`, `operation`, `value`, `category`) VALUES (?, ?, ?, ?)",
                            (self.get_user_id(user_id),
                             operation == "+",
                             amount, category))
        return self.conn.commit()

    def get_records(self, user_id, data_begin, end_date):
        """Получаем историю о доходах/расходах"""
        result = self.cursor.execute(
            "SELECT `date`, case when `operation` = 0 then -`value` else `value` end, `category`  FROM `records` "
            "WHERE `users_id` "
            "= ? AND `date` >= ? AND "
            "`date` <= ?",
            (self.get_user_id(user_id), data_begin, end_date))

        return result.fetchall()

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()

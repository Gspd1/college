# # create_db.py
# import pymysql
# from config import host, user, password
#
#
# def create_database():
#     """Создание базы данных и всех необходимых таблиц"""
#     try:
#         conn = pymysql.connect(
#             host=host,
#             user=user,
#             password=password,
#             cursorclass=pymysql.cursors.DictCursor
#         )
#         cursor = conn.cursor()
#
#         # Создаем базу данных
#         cursor.execute("CREATE DATABASE IF NOT EXISTS `nail-salon`")
#
#         conn.select_db('nail-salon')
#
#         # Таблица мастеров
#         cursor.execute("""
#         CREATE TABLE IF NOT EXISTS masters (
#             id INTEGER AUTO_INCREMENT PRIMARY KEY,
#             surname TEXT NOT NULL,
#             name TEXT NOT NULL,
#             patronymic TEXT NOT NULL
#         );
#         """)
#
#         # Таблица клиентов
#         cursor.execute("""
#         CREATE TABLE IF NOT EXISTS clients (
#             id INTEGER AUTO_INCREMENT PRIMARY KEY,
#             surname TEXT COMMENT 'Фамилия',
#             name TEXT NOT NULL COMMENT 'Имя',
#             patronymic TEXT COMMENT 'Отчество',
#             phone VARCHAR(12) NOT NULL UNIQUE,
#             CONSTRAINT chk_phone_format CHECK (phone REGEXP '^\\\\+[0-9]{11}$')
#         );
#         """)
#
#         # Таблица услуг
#         cursor.execute("""
#         CREATE TABLE IF NOT EXISTS services (
#             id INTEGER AUTO_INCREMENT PRIMARY KEY,
#             name TEXT COMMENT 'Наименование',
#             duration INTEGER NOT NULL CHECK (duration > 0) COMMENT 'Длительность в минутах',
#             cost INTEGER NOT NULL CHECK (cost > 0) COMMENT 'Стоимость',
#             master_id INTEGER NOT NULL,
#             FOREIGN KEY (master_id) REFERENCES masters(id) ON DELETE CASCADE
#         );
#         """)
#
#         # Таблица расписания мастеров по дням недели
#         cursor.execute("""
#         CREATE TABLE IF NOT EXISTS master_schedule (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             master_id INT NOT NULL,
#             day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 1 AND 7), -- 1=Пн, 7=Вс
#             work_date DATE NOT NULL, -- Конкретная дата
#             start_time TIME NOT NULL,
#             end_time TIME NOT NULL,
#             FOREIGN KEY (master_id) REFERENCES masters(id) ON DELETE CASCADE,
#             UNIQUE KEY unique_master_day (master_id, work_date, start_time)
#         );
#         """)
#
#
#         # cursor.execute("DROP TABLE IF EXISTS time_slots")  # И зависимую таблицу тоже
#         #
#         # cursor.execute("DROP TABLE IF EXISTS appointments")
#
#
#         # Таблица записей
#         cursor.execute("""
#         CREATE TABLE IF NOT EXISTS appointments (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             client_id INT NOT NULL,
#             master_id INT NOT NULL,
#             service_id INT NOT NULL,
#             appointment_date DATE NOT NULL,
#             start_time TIME NOT NULL,
#             end_time TIME NOT NULL,
#             total_price DECIMAL(10,2) NOT NULL DEFAULT 0,
#             status ENUM('Выполнено', 'Отменено', 'Ожидается', 'В процессе') DEFAULT 'Ожидается',
#             created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
#             FOREIGN KEY (master_id) REFERENCES masters(id) ON DELETE CASCADE,
#             FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
#         );
#         """)
#
#         # Таблица блокировок времени (для отмененных или недоступных слотов)
#         cursor.execute("""
#         CREATE TABLE IF NOT EXISTS time_slots (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             master_id INT NOT NULL,
#             slot_date DATE NOT NULL,
#             start_time TIME NOT NULL,
#             end_time TIME NOT NULL,
#             is_available BOOLEAN DEFAULT TRUE,
#             appointment_id INT NULL,
#             FOREIGN KEY (master_id) REFERENCES masters(id) ON DELETE CASCADE,
#             FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL
#         );
#         """)
#
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS master_services (
#                 id INT AUTO_INCREMENT PRIMARY KEY,
#                 master_id INT NOT NULL,
#                 service_id INT NOT NULL,
#                 FOREIGN KEY (master_id) REFERENCES masters(id) ON DELETE CASCADE,
#                 FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE,
#                 UNIQUE KEY unique_master_service (master_id, service_id)
#         );
#         """)
#
#         conn.commit()
#         print("База данных и таблицы успешно созданы!")
#         return True
#
#     except Exception as ex:
#         print(f"Ошибка при создании БД: {ex}")
#         return False
#     finally:
#         if 'conn' in locals():
#             conn.close()
#
#
# if __name__ == "__main__":
#     create_database()


# create_db.py - исправленный
import pymysql
from config import host, user, password, db_name


def create_database():
    """Проверка подключения к существующей БД (не создает новую БД)"""
    try:
        # Подключаемся к существующей БД
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,  # Используем существующую БД
            cursorclass=pymysql.cursors.DictCursor
        )

        cursor = conn.cursor()

        # Проверяем существование необходимых таблиц
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        table_names = [list(table.values())[0] for table in tables]
        print(f"✓ Подключение к базе данных '{db_name}' успешно")
        print(f"✓ Найдено таблиц: {len(table_names)}")

        # Проверяем наличие нужных таблиц
        required_tables = ['masters', 'clients', 'services', 'appointments', 'master_schedule']
        missing_tables = [table for table in required_tables if table not in table_names]

        if missing_tables:
            print(f"⚠ Отсутствуют таблицы: {missing_tables}")
        else:
            print("✓ Все необходимые таблицы присутствуют")

        conn.close()
        return True

    except Exception as ex:
        print(f"✗ Ошибка при подключении к БД: {ex}")
        print("\nВозможные причины:")
        print(f"1. База данных '{db_name}' не существует на сервере")
        print("2. У пользователя нет прав на доступ к этой БД")
        print("3. Неправильный пароль")
        return False


if __name__ == "__main__":
    create_database()
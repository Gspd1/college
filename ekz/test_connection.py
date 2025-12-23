# test_connection.py - для проверки подключения
import pymysql
from config import host, user, password, port, db_name

try:
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )

    print("✓ Успешное подключение к базе данных!")

    # Проверяем таблицы
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✓ Найдено таблиц: {len(tables)}")

        # Показываем первые 10 таблиц
        print("\nПервые 10 таблиц:")
        for i, table in enumerate(tables[:10]):
            print(f"  {i + 1}. {list(table.values())[0]}")

        if len(tables) > 10:
            print(f"  ... и еще {len(tables) - 10} таблиц")

    connection.close()

except pymysql.Error as e:
    print(f"✗ Ошибка подключения: {e}")
    print("\nВозможные причины:")
    print("1. Неправильный пароль")
    print("2. Нет доступа с вашего IP")
    print("3. Сервер не доступен")
    print("4. Не установлен pymysql (pip install pymysql)")
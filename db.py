import pymysql
from datetime import datetime, timedelta, date
from config import *


def get_connection():
    """Создание соединения с базой данных"""
    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )


# ========== МАСТЕРА ==========
def get_masters():
    """Получение списка всех мастеров"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM masters ORDER BY surname, name")
            return cursor.fetchall()


def add_master(surname, name, patronymic):
    """Добавление нового мастера"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO masters (surname, name, patronymic) VALUES (%s, %s, %s)",
                (surname, name, patronymic)
            )
            conn.commit()
            return cursor.lastrowid


def update_master(master_id, surname, name, patronymic):
    """Обновление информации о мастере"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE masters SET surname=%s, name=%s, patronymic=%s WHERE id=%s",
                (surname, name, patronymic, master_id)
            )
            conn.commit()
            return cursor.rowcount


def delete_master(master_id):
    """Удаление мастера"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM masters WHERE id=%s", (master_id,))
            conn.commit()
            return cursor.rowcount


# ========== КЛИЕНТЫ ==========
def get_clients():
    """Получение списка всех клиентов"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, 
                       CONCAT(COALESCE(surname, ''), ' ', name, ' ', COALESCE(patronymic, '')) as full_name,
                       phone 
                FROM clients 
                ORDER BY surname, name
            """)
            return cursor.fetchall()


def get_client_by_id(client_id):
    """Получение клиента по ID"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM clients WHERE id=%s", (client_id,))
            return cursor.fetchone()


def add_client(surname, name, patronymic, phone):
    """Добавление нового клиента"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO clients (surname, name, patronymic, phone) VALUES (%s, %s, %s, %s)",
                (surname, name, patronymic, phone)
            )
            conn.commit()
            return cursor.lastrowid


def update_client(client_id, surname, name, patronymic, phone):
    """Обновление информации о клиенте"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE clients SET surname=%s, name=%s, patronymic=%s, phone=%s WHERE id=%s",
                (surname, name, patronymic, phone, client_id)
            )
            conn.commit()
            return cursor.rowcount


def delete_client(client_id):
    """Удаление клиента"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM clients WHERE id=%s", (client_id,))
            conn.commit()
            return cursor.rowcount


# ========== УСЛУГИ ==========
def get_services():
    """Получение списка всех услуг с именем мастера"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT s.*, 
                       CONCAT(m.surname, ' ', m.name, ' ', COALESCE(m.patronymic, '')) as master_name
                FROM services s
                JOIN masters m ON s.master_id = m.id
                ORDER BY s.name
            """)
            return cursor.fetchall()


def get_services_by_master(master_id):
    """Получение услуг конкретного мастера"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM services WHERE master_id=%s ORDER BY name", (master_id,))
            return cursor.fetchall()


def add_service(name, duration, cost, master_id):
    """Добавление новой услуги"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO services (name, duration, cost, master_id) VALUES (%s, %s, %s, %s)",
                (name, duration, cost, master_id)
            )
            conn.commit()
            return cursor.lastrowid


def update_service(service_id, name, duration, cost, master_id):
    """Обновление информации об услуге"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE services SET name=%s, duration=%s, cost=%s, master_id=%s WHERE id=%s",
                (name, duration, cost, master_id, service_id)
            )
            conn.commit()
            return cursor.rowcount


def delete_service(service_id):
    """Удаление услуги"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM services WHERE id=%s", (service_id,))
            conn.commit()
            return cursor.rowcount


# ========== РАСПИСАНИЕ МАСТЕРОВ ==========
def get_master_schedule(master_id, week_start_date):
    """Получение расписания мастера на неделю"""
    week_end_date = week_start_date + timedelta(days=6)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM master_schedule 
                WHERE master_id=%s AND work_date BETWEEN %s AND %s
                ORDER BY work_date, start_time
            """, (master_id, week_start_date, week_end_date))
            return cursor.fetchall()


def set_master_schedule(master_id, day_data):
    """Установка расписания мастера на неделю"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Удаляем старое расписание на эти дни
            if day_data:
                dates = [d['work_date'] for d in day_data]
                placeholders = ','.join(['%s'] * len(dates))
                cursor.execute(
                    f"DELETE FROM master_schedule WHERE master_id=%s AND work_date IN ({placeholders})",
                    [master_id] + dates
                )

                # Добавляем новое расписание
                for day in day_data:
                    cursor.execute("""
                        INSERT INTO master_schedule (master_id, day_of_week, work_date, start_time, end_time)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (master_id, day['day_of_week'], day['work_date'], day['start_time'], day['end_time']))

                conn.commit()
                return len(day_data)
            return 0


def get_master_working_dates(master_id):
    """Получение всех дат, когда работает мастер"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT work_date FROM master_schedule 
                WHERE master_id=%s 
                ORDER BY work_date
            """, (master_id,))
            results = cursor.fetchall()
            return [row['work_date'] for row in results]


# ========== ДОСТУПНОЕ ВРЕМЯ ==========
def get_available_time_slots(master_id, selected_date):
    """Получение доступных временных слотов мастера на выбранную дату"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Получаем расписание мастера на эту дату
            cursor.execute("""
                SELECT start_time, end_time FROM master_schedule 
                WHERE master_id=%s AND work_date=%s
            """, (master_id, selected_date))

            schedule = cursor.fetchone()
            if not schedule:
                return []  # Мастер не работает в этот день

            # Получаем существующие записи на эту дату
            cursor.execute("""
                SELECT start_time, end_time FROM appointments 
                WHERE master_id=%s AND appointment_date=%s AND status NOT IN ('Отменено')
            """, (master_id, selected_date))

            booked_slots = cursor.fetchall()

            # Генерируем доступные слоты
            available_slots = []
            start_time_str = str(schedule['start_time'])
            end_time_str = str(schedule['end_time'])

            # Проверяем формат времени
            if len(start_time_str) == 8:  # HH:MM:SS
                start_time = datetime.strptime(start_time_str, '%H:%M:%S')
                end_time = datetime.strptime(end_time_str, '%H:%M:%S')
            else:
                start_time = datetime.strptime(start_time_str, '%H:%M')
                end_time = datetime.strptime(end_time_str, '%H:%M')

            current_time = start_time
            slot_duration = timedelta(minutes=30)  # Длительность слота

            while current_time + slot_duration <= end_time:
                slot_start = current_time.time()
                slot_end = (current_time + slot_duration).time()

                # Проверяем, не занят ли слот
                is_available = True
                for booked in booked_slots:
                    booked_start = booked['start_time']
                    booked_end = booked['end_time']

                    # Проверка на пересечение временных интервалов
                    if not (slot_end <= booked_start or slot_start >= booked_end):
                        is_available = False
                        break

                if is_available:
                    available_slots.append({
                        'start': slot_start.strftime('%H:%M'),
                        'end': slot_end.strftime('%H:%M')
                    })

                current_time += slot_duration

            return available_slots


# ========== ЗАПИСИ ==========
# Исправляем функцию get_appointments() в db.py:
def get_appointments():
    """Получение всех записей с деталями"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT a.*, 
                       CONCAT(c.surname, ' ', c.name, ' ', COALESCE(c.patronymic, '')) as client_name,
                       c.phone as client_phone,
                       CONCAT(m.surname, ' ', m.name, ' ', COALESCE(m.patronymic, '')) as master_name,
                       s.name as service_name,
                       s.cost as service_price
                FROM appointments a
                JOIN clients c ON a.client_id = c.id
                JOIN masters m ON a.master_id = m.id
                JOIN services s ON a.service_id = s.id
                ORDER BY a.appointment_date DESC, a.start_time DESC
            """)
            return cursor.fetchall()

# Исправляем функцию get_appointments_by_date() в db.py:
def get_appointments_by_date(appointment_date):
    """Получение записей на конкретную дату"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT a.*, 
                       CONCAT(c.surname, ' ', c.name, ' ', COALESCE(c.patronymic, '')) as client_name,
                       CONCAT(m.surname, ' ', m.name, ' ', COALESCE(m.patronymic, '')) as master_name,
                       s.name as service_name
                FROM appointments a
                JOIN clients c ON a.client_id = c.id
                JOIN masters m ON a.master_id = m.id
                JOIN services s ON a.service_id = s.id
                WHERE a.appointment_date=%s
                ORDER BY a.start_time
            """, (appointment_date,))
            return cursor.fetchall()


def add_appointment(client_id, master_id, service_id, appointment_date, start_time, end_time):
    """Добавление новой записи"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Получаем стоимость услуги
            cursor.execute("SELECT cost FROM services WHERE id=%s", (service_id,))
            service = cursor.fetchone()
            total_price = service['cost'] if service else 0

            cursor.execute("""
                INSERT INTO appointments 
                (client_id, master_id, service_id, appointment_date, start_time, end_time, total_price, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Ожидается')
            """, (client_id, master_id, service_id, appointment_date, start_time, end_time, total_price))

            conn.commit()
            return cursor.lastrowid


def update_appointment(appointment_id, client_id, master_id, service_id, appointment_date, start_time, end_time,
                       status):
    """Обновление записи"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Получаем стоимость услуги
            cursor.execute("SELECT cost FROM services WHERE id=%s", (service_id,))
            service = cursor.fetchone()
            total_price = service['cost'] if service else 0

            cursor.execute("""
                UPDATE appointments 
                SET client_id=%s, master_id=%s, service_id=%s, 
                    appointment_date=%s, start_time=%s, end_time=%s,
                    total_price=%s, status=%s
                WHERE id=%s
            """, (client_id, master_id, service_id, appointment_date, start_time, end_time, total_price, status,
                  appointment_id))

            conn.commit()
            return cursor.rowcount


def delete_appointment(appointment_id):
    """Удаление записи"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM appointments WHERE id=%s", (appointment_id,))
            conn.commit()
            return cursor.rowcount


# ========== ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ==========
def validate_phone(phone):
    """Проверка формата телефона"""
    import re
    pattern = r'^\+[0-9]{11}$'
    return re.match(pattern, phone) is not None


def format_client_name(client):
    """Форматирование имени клиента"""
    parts = []
    if client.get('surname'):
        parts.append(client['surname'])
    if client.get('name'):
        parts.append(client['name'])
    if client.get('patronymic'):
        parts.append(client['patronymic'])
    return ' '.join(parts) if parts else "Не указано"



def get_master_services(master_id):
    """Получение услуг, которые предоставляет конкретный мастер"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT s.* 
                FROM services s
                JOIN master_services ms ON s.id = ms.service_id
                WHERE ms.master_id = %s
                ORDER BY s.name
            """, (master_id,))
            return cursor.fetchall()

def add_master_service(master_id, service_id):
    """Добавление услуги мастеру"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO master_services (master_id, service_id) VALUES (%s, %s)",
                (master_id, service_id)
            )
            conn.commit()
            return cursor.lastrowid

def remove_master_service(master_id, service_id):
    """Удаление услуги у мастера"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM master_services WHERE master_id=%s AND service_id=%s",
                (master_id, service_id)
            )
            conn.commit()
            return cursor.rowcount

def get_all_master_services():
    """Получение всех связей мастеров и услуг"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT ms.*, 
                       CONCAT(m.surname, ' ', m.name) as master_name,
                       s.name as service_name
                FROM master_services ms
                JOIN masters m ON ms.master_id = m.id
                JOIN services s ON ms.service_id = s.id
                ORDER BY master_name, service_name
            """)
            return cursor.fetchall()
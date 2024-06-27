import sqlite3

def connection_to_database():
    # Підключення до бази даних
    conn = sqlite3.connect('database.db')

    # Створення курсору
    cursor = conn.cursor()

    # Виконання запиту
    query = "SELECT dish_name, dish_price FROM Menu WHERE category = 'Закуски';"
    cursor.execute(query)

    # Витяг даних
    results = cursor.fetchall()

    # Обробка результатів
    for row in results:
        print(row[0], row[1])

    # Закриття курсору та з'єднання
    cursor.close()
    conn.close()

# Виклик функції для перевірки
connection_to_database()

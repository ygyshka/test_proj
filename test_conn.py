from sqlalchemy import create_engine, text

# Укажите данные для подключения к PostgreSQL
db_user = 'postgres'
db_password = 'mysecretpassword'
db_host = 'localhost'
db_port = '5433'
db_name = 'music_shop'
# The meaning of life
# Формируем строку подключения
connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# Создаем подключение к базе данных
engine = create_engine(connection_string)

# Открываем соединение
with engine.connect() as conn:
# SQL запрос для получения версии PostgreSQL
    query = text("SELECT version();")

# Выполняем запрос
    result = conn.execute(query)

# Получаем результат
    version = result.fetchone()[0]

    print("PostgreSQL version:", version)

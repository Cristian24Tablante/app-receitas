import mysql.connector

def get_db():
    return mysql.connector.connect(
        host='tini.click',
        user='spoiler_com_sabor',
        password='4287816f7bc22c82a83f70ad492266db',
        database='spoiler_com_sabor'
    )
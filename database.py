import MySQLdb
from MySQLdb.cursors import DictCursor

def get_db():
    return MySQLdb.connect(
        host='tini.click',
        user='spoiler_com_sabor',
        passwd='4287816f7bc22c82a83f70ad492266db',
        db='spoiler_com_sabor',
        cursorclass=DictCursor
    )
    
print("Conexión a la base de datos establecida.")
    
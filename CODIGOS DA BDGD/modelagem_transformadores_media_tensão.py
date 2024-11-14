import psycopg2
import py_dss_interface
import os

dss = py_dss_interface.DSSDLL()

class DataBaseQuery:
    def __init__(self, dbhost, dbport, dbdbname, dbuser, dbpassword):
        """Inicializa os paramêmtros de conexão"""
        self.host = dbhost
        self.

# Uso da classe
if __name__ == "__main__":
    # Parâmetros de conexão
    host = 'localhost'
    port = '5432'
    user = 'iuri'
    password = 'aa11bb22'

    # Cria uma instância da classe DataBaseQuery
    db_query = DataBaseQuery(host, port, user, password)


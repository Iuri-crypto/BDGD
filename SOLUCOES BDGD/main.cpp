#include <iostream>
#include <libpq-fe.h>

void printResults(PGresult *res);

int main() {
    // Configurações de conexão ao banco de dados PostgreSQL
    const char *conninfo = "host=localhost port=5432 dbname=bdgd user=iuri password=aa11bb22";

    // Conecta ao banco de dados PostgreSQL
    PGconn *conn = PQconnectdb(conninfo);

    // Verifica se a conexão foi bem-sucedida
    if (PQstatus(conn) != CONNECTION_OK) {
        std::cerr << "Erro ao conectar ao banco de dados: " << PQerrorMessage(conn) << std::endl;
        PQfinish(conn);
        return 1;
    }

    // Executa a consulta à tabela SSDMT
    PGresult *res = PQexec(conn, "SELECT * FROM ssdmt;");

    // Verifica se a consulta foi bem-sucedida
    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        std::cerr << "Erro ao executar a consulta: " << PQerrorMessage(conn) << std::endl;
        PQclear(res);
        PQfinish(conn);
        return 1;
    }

    // Exibe os resultados
    printResults(res);

    // Limpa e fecha a conexão
    PQclear(res);
    PQfinish(conn);

    std::cout << "Consulta à tabela ssdmt concluída com sucesso." << std::endl;

    return 0;
}

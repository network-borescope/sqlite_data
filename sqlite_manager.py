import sqlite3

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        create_database(db_file, conn)
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)


def create_database(DATABASE, conn = None):
    kv_table = """ CREATE TABLE "kv" (
                                "id" INTEGER NOT NULL,
                                "k" VARCHAR(100) NOT NULL,
                                "txt" TEXT NULL,
                                "bin" BLOB NULL,
                                "aux" TXT NULL,
                                PRIMARY KEY ("id", "k")
                            ); """

    tsx_table = """ CREATE TABLE "tsx" (
                        "id" INTEGER NOT NULL,
                        "tm" INTEGER NOT NULL,
                        "text" TEXT NOT NULL,
                        PRIMARY KEY ("id", "tm")
                    ); """

    close_at_end = False
    # create a database connection
    if conn is None:
        conn = create_connection(DATABASE)
        close_at_end = True

    # create tables
    if conn is not None:
        # create table
        create_table(conn, kv_table)
        create_table(conn, tsx_table)

        if close_at_end: conn.close()
    else:
        print("Error! cannot create the database connection.")


def insert_row_tsx(conn, ID, epoch, buf):
    sql = "INSERT INTO TSX (ID, TM, TEXT) VALUES ({0}, {1}, '{2}') " + \
              " on conflict(id, tm) do update set text = text || '{2}';"
    #sql = ''' INSERT INTO TSX (ID, TM, TEXT) VALUES (?, ?, ?)'''

    s = sql.format(ID, epoch, buf)

    cur = conn.cursor()
    #cur.execute(sql, (ip, time, time, client_id))
    cur.execute(s)
    conn.commit()

    return cur.rowcount


def insert_row_kv(conn, ID, k, txt=None, bin=None, aux=None):
    #sql = "INSERT INTO KV (ID, k, txt, bin, aux) VALUES ({0}, '{1}', {2}, {3}, {4}) " + \
              #" on conflict(id, k) do update set txt = txt || {2};"
    sql = '''INSERT INTO KV (ID, k, txt, bin, aux) VALUES (?, ?, ?, ?, ?) on conflict(id,k) do update set txt = txt || ?'''

    #s = sql.format(ID, k, txt, bin, aux)

    cur = conn.cursor()
    cur.execute(sql, (ID, k, txt, bin, aux, txt))
    #print(s)
    #cur.execute(s)
    conn.commit()

    return cur.rowcount


if __name__ == "__main__":
    create_database("db_timeseries.db")
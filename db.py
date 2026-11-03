import sqlite3
import os

DATABASE_NAME = "tarefas.db"


def get_db_path():
    """Returns the absolute path for the database file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, DATABASE_NAME)


def connect_db():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(get_db_path())
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None


def create_table():
    """Creates the tarefas table if it doesn't already exist."""
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tarefas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descricao TEXT NOT NULL,
                    status INTEGER NOT NULL DEFAULT 0,
                    data_tarefa TEXT NOT NULL
                )
            """)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao criar tabela: {e}")
        finally:
            conn.close()


def insert_task(description, date):
    """Inserts a new task into the database."""
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tarefas (descricao, status, data_tarefa) VALUES (?, ?, ?)",
                (description, 0, date),
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao inserir tarefa: {e}")
            return None
        finally:
            conn.close()


def update_task_status(task_id, status):
    """Updates the status of a task."""
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tarefas SET status = ? WHERE id = ?", (status, task_id)
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao atualizar status da tarefa: {e}")
        finally:
            conn.close()


def select_tasks_by_date(date):
    """Selects all tasks for a specific date."""
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, descricao, status, data_tarefa FROM tarefas WHERE data_tarefa = ? ORDER BY id ASC",
                (date,),
            )
            tasks = cursor.fetchall()
            return [dict(task) for task in tasks]
        except sqlite3.Error as e:
            print(f"Erro ao selecionar tarefas por data: {e}")
            return []
        finally:
            conn.close()


def delete_task(task_id):
    """Deletes a task from the database."""
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tarefas WHERE id = ?", (task_id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao excluir tarefa: {e}")
        finally:
            conn.close()


if __name__ == "__main__":
    create_table()
    print(f"Database initialized at: {get_db_path()}")

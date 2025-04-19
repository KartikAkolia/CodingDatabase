import os
import subprocess
import shutil
import mysql.connector
import getpass
from functools import wraps

# Decorator for retrying DB operations on connection errors
def with_retry(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except mysql.connector.errors.OperationalError:
            try:
                self.db.reconnect(attempts=1, delay=2)
            except Exception:
                # If reconnect fails, re-raise original
                raise
            return fn(self, *args, **kwargs)
    return wrapper

class Scoreboard:
    # Map game names to Inventory IDs
    GAME_ID = {
        "UNO":    1,
        "Chess":  2,
        "Carrom": 3,
    }

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        port: int = 3306,
        use_inventory: bool = True
    ):
        # Establish initial connection
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        self.use_inventory = use_inventory

    @with_retry
    def _get_table(self, game: str) -> str:
        if self.use_inventory:
            tbl = self._lookup_inventory(game)
            if tbl:
                return tbl
        if game in self.GAME_ID:
            return game
        raise ValueError(f"Unknown game: {game!r}")

    @with_retry
    def _lookup_inventory(self, game: str) -> str | None:
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT NAME FROM Inventory WHERE ID = %s",
                (self.GAME_ID.get(game),)
            )
            row = cur.fetchone()
        return row[0] if row else None

    @with_retry
    def add_score(self, game: str, player_name: str, score: int) -> None:
        tbl = self._get_table(game)
        code = player_name[0]
        with self.db.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) FROM `{tbl}` WHERE Code = %s",
                (code,)
            )
            (count,) = cur.fetchone()
            if count:
                print(f"Record already exists for code {code}")
                return
            cur.execute(
                f"INSERT INTO `{tbl}` (Name, Score, Code) VALUES (%s, %s, %s)",
                (player_name, score, code)
            )
        self.db.commit()
        print(f"Inserted {player_name} with score {score} in {tbl}")

    @with_retry
    def show_scores(self, game: str) -> None:
        tbl = self._get_table(game)
        with self.db.cursor() as cur:
            cur.execute(f"SELECT Name, Score, Code FROM `{tbl}`")
            rows = cur.fetchall()
        if not rows:
            print(f"No scores found in {tbl}")
            return
        for name, score, code in rows:
            print(f"{name:<15} {score:>5}   code={code}")

    @with_retry
    def update_score(self, game: str, player_name: str, delta: int = 1) -> None:
        tbl = self._get_table(game)
        code = player_name[0]
        with self.db.cursor() as cur:
            cur.execute(
                f"UPDATE `{tbl}` SET Score = Score + %s WHERE Code = %s",
                (delta, code)
            )
        self.db.commit()
        print(f"Updated {tbl} code {code} by {delta}")

    @with_retry
    def reset_scores(self, game: str) -> None:
        tbl = self._get_table(game)
        with self.db.cursor() as cur:
            cur.execute(f"UPDATE `{tbl}` SET Score = 0")
        self.db.commit()
        print(f"All scores reset in {tbl}")

    @with_retry
    def clear_table(self, game: str) -> None:
        tbl = self._get_table(game)
        with self.db.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE `{tbl}`")
        self.db.commit()
        print(f"All records deleted from {tbl}")

    @with_retry
    def log_and_clear(self, game: str, log_table: str = "Logs") -> None:
        tbl = self._get_table(game)
        today = "CURDATE()"
        with self.db.cursor() as cur:
            cur.execute(f"DELETE FROM `{log_table}` WHERE Logdate = {today}")
            cur.execute(
                f"INSERT INTO `{log_table}` (Name, Score, Logdate) "
                f"SELECT Name, Score, {today} FROM `{tbl}`"
            )
            cur.execute(f"UPDATE `{tbl}` SET Score = 0")
        self.db.commit()
        print(f"Logged and cleared scores for {game}")

class ServiceManager:
    def __init__(self, db_conn: mysql.connector.MySQLConnection):
        self.db = db_conn

    @with_retry
    def check_service(self, name: str) -> None:
        running = subprocess.call(
            ["systemctl", "is-active", "--quiet", name]
        ) == 0 if shutil.which("systemctl") else \
            subprocess.call(
                ["service", name, "status"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            ) == 0
        status_str = "Running" if running else "Not Running"
        needs_restart = "N" if running else "Y"
        name_db = name.upper()[:20]

        with self.db.cursor() as cur:
            cur.execute("DELETE FROM Services WHERE Name = %s", (name_db,))
            cur.execute(
                "INSERT INTO Services (Name, Status, Restart) VALUES (%s, %s, %s)",
                (name_db, status_str, needs_restart)
            )
        self.db.commit()
        print(f"{name_db}: {status_str}")

    def control(self, name: str, action: str) -> None:
        if action not in ("start", "stop", "restart", "status"):
            raise ValueError(f"Invalid action: {action!r}")
        cmd = ["systemctl", action, name] if shutil.which("systemctl") else ["service", name, action]
        print("Executing:", " ".join(cmd))
        subprocess.call(cmd)


def main():
    # Prompt for MySQL credentials at runtime
    host = input("MySQL Host (default: localhost): ").strip() or "localhost"
    port_input = input("MySQL Port (default: 3306): ").strip()
    port = int(port_input) if port_input else 3306
    user = input("MySQL Username (default: kartik): ").strip() or "kartik"
    password = getpass.getpass("MySQL Password: ")
    database = input("Database Name (default: KARTIK): ").strip() or "KARTIK"

    # Initialize and validate connection
    try:
        sb = Scoreboard(host, user, password, database, port)
        # quick validation
        with sb.db.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
    except Exception as e:
        print("Could not connect to database:", e)
        return

    sm = ServiceManager(sb.db)
    print("Connected to database successfully.")

    game = input("Which game? UNO, Chess, Carrom: ").strip()

    while True:
        print("""
1) Add score   2) Show scores   3) Update score   4) Reset scores
5) Clear table 6) Log & clear   7) Service status   8) Control service
9) SQL prompt  0) Exit
""")
        cmd = input("> ").strip()

        if cmd == "0":
            break
        elif cmd == "1":
            name = input("Player name: ").strip()
            score = int(input("Score: ").strip())
            sb.add_score(game, name, score)
        elif cmd == "2":
            sb.show_scores(game)
        elif cmd == "3":
            name = input("Player name: ").strip()
            sb.update_score(game, name)
        elif cmd == "4":
            sb.reset_scores(game)
        elif cmd == "5":
            sb.clear_table(game)
        elif cmd == "6":
            sb.log_and_clear(game)
        elif cmd == "7":
            svc = input("Which service to check? ").strip()
            sm.check_service(svc)
        elif cmd == "8":
            svc = input("Service name: ").strip()
            action = input("Action (start/stop/restart/status): ").strip()
            sm.control(svc, action)
        elif cmd == "9":
            # Interactive SQL prompt mode
            conn = sb.db
            conn.start_transaction()
            session_log = []
            while True:
                sql = input("SQL> ").strip()
                if sql.lower() in (r"\\q", "exit"):
                    break
                if not sql.endswith(";"):
                    print("Please end each statement with a semicolon.")
                    continue
                try:
                    with conn.cursor() as c:
                        c.execute(sql)
                        if c.with_rows:
                            rows = c.fetchall()
                            for row in rows:
                                print(row)
                            session_log.append(("OK", sql, rows))
                        else:
                            print(f"{c.rowcount} rows affected.")
                            session_log.append(("OK", sql, f"{c.rowcount} rows"))
                except Exception as e:
                    print("Error:", e)
                    session_log.append(("ERR", sql, str(e)))
            # Commit or rollback
            if input("Commit changes? [y/N]: ").strip().lower() == "y":
                conn.commit()
                print("Transaction committed.")
            else:
                conn.rollback()
                print("All changes rolled back.")
            # Log save/discard
            if input("Save SQL log to file? [Y/n]: ").strip().lower() != "n":
                logfile = "sql_session.log"
                with open(logfile, "w") as f:
                    for status, stmt, res in session_log:
                        f.write(f"{status}\t{stmt}\t{res}\n")
                print(f"Log written to {logfile}")
            else:
                print("Log discarded.")
        else:
            print("Unknown choice.")

if __name__ == "__main__":
    main()

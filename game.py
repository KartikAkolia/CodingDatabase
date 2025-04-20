#!/usr/bin/env python3

import re
import subprocess
import shutil
import mysql.connector
import getpass
import logging
import sys
import tty
import termios
from functools import wraps

# --- External Live-Reload Instructions ---
# To auto-restart on code changes, install watchdog and run:
#   pip install watchdog
#   watchmedo auto-restart --patterns="*.py" --recursive -- python3 game.py

# --- Structured Logging Setup ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
fh = logging.FileHandler('game.log')
fh.setFormatter(formatter)
logger.addHandler(fh)

# --- Retry Decorator for DB Operations ---
def with_retry(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except mysql.connector.errors.OperationalError as e:
            logger.warning(f"DB OperationalError: {e}. Reconnecting...")
            try:
                self.db.reconnect(attempts=1, delay=2)
                logger.info("Reconnected to database.")
            except Exception as re_err:
                logger.error(f"Reconnect failed: {re_err}")
                raise
            return fn(self, *args, **kwargs)
    return wrapper

# --- Helper for Pretty-Printing Query Results ---
def print_table(columns, rows):
    widths = [len(col) for col in columns]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    sep = '+' + '+'.join('-' * (w + 2) for w in widths) + '+'
    header = '|' + '|'.join(f' {columns[i].ljust(widths[i])} ' for i in range(len(columns))) + '|'
    print(sep)
    print(header)
    print(sep)
    for row in rows:
        line = '|' + '|'.join(f' {str(row[i]).ljust(widths[i])} ' for i in range(len(columns))) + '|'
        print(line)
    print(sep)

# --- Scoreboard Class ---
class Scoreboard:
    GAME_ID = {"UNO": 1, "Chess": 2, "Carrom": 3}

    def __init__(self, host, user, password, database, port=3306, use_inventory=True):
        self.host, self.user, self.password, self.database, self.port = host, user, password, database, port
        self.use_inventory = use_inventory
        self.connect()

    def connect(self):
        self.db = mysql.connector.connect(
            host=self.host, user=self.user, password=self.password,
            database=self.database, port=self.port
        )
        logger.info("Database connection established.")

    @with_retry
    def _get_table(self, game):
        if self.use_inventory:
            tbl = self._lookup_inventory(game)
            if tbl:
                return tbl
        if game in self.GAME_ID:
            return game
        raise ValueError(f"Unknown game: {game!r}")

    @with_retry
    def _lookup_inventory(self, game):
        with self.db.cursor() as cur:
            cur.execute("SELECT NAME FROM Inventory WHERE ID = %s", (self.GAME_ID[game],))
            row = cur.fetchone()
        return row[0] if row else None

    @with_retry
    def add_score(self, game, player_name, score):
        tbl = self._get_table(game)
        code = player_name[0]
        with self.db.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM `{tbl}` WHERE Code = %s", (code,))
            (count,) = cur.fetchone()
            if count:
                logger.info(f"Record exists for code {code}")
                return
            cur.execute(f"INSERT INTO `{tbl}` (Name,Score,Code) VALUES (%s,%s,%s)", (player_name, score, code))
        self.db.commit()
        logger.info(f"Inserted {player_name} ({code}) with score {score} into {tbl}")

    @with_retry
    def show_scores(self, game):
        tbl = self._get_table(game)
        with self.db.cursor() as cur:
            cur.execute(f"SELECT Name, Score, Code FROM `{tbl}`")
            rows = cur.fetchall()
            if not rows:
                logger.info(f"No scores in {tbl}")
                return
            columns = [d[0] for d in cur.description]
        print_table(columns, rows)

    @with_retry
    def update_score(self, game, player_name, delta=1):
        tbl = self._get_table(game)
        code = player_name[0]
        with self.db.cursor() as cur:
            cur.execute(f"UPDATE `{tbl}` SET Score=Score+%s WHERE Code=%s", (delta, code))
        self.db.commit()
        logger.info(f"Updated {tbl} code {code} by {delta}")

    @with_retry
    def reset_scores(self, game):
        tbl = self._get_table(game)
        with self.db.cursor() as cur:
            cur.execute(f"UPDATE `{tbl}` SET Score=0")
        self.db.commit()
        logger.info(f"Reset scores in {tbl}")

    @with_retry
    def clear_table(self, game):
        tbl = self._get_table(game)
        with self.db.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE `{tbl}`")
        self.db.commit()
        logger.info(f"Cleared table {tbl}")

    @with_retry
    def log_and_clear(self, game, log_table="Logs"):
        tbl = self._get_table(game)
        today = "CURDATE()"
        with self.db.cursor() as cur:
            cur.execute(f"DELETE FROM `{log_table}` WHERE Logdate={today}")
            cur.execute(
                f"INSERT INTO `{log_table}` (Name,Score,Logdate) "
                f"SELECT Name,Score,{today} FROM `{tbl}`"
            )
            cur.execute(f"UPDATE `{tbl}` SET Score=0")
        self.db.commit()
        logger.info(f"Logged and cleared {tbl} into {log_table}")

# --- Service Manager Class ---
class ServiceManager:
    VALID_ACTIONS = {"start","stop","restart","status"}
    NAME_PATTERN = re.compile(r'^[\w\-]+$')

    def __init__(self, db_conn):
        self.db = db_conn

    @with_retry
    def check_service(self, name):
        if not self.NAME_PATTERN.match(name):
            raise ValueError("Invalid service name")
        use_systemctl = shutil.which("systemctl") is not None
        if use_systemctl:
            running = subprocess.call(["systemctl","is-active","--quiet",name]) == 0
        else:
            running = subprocess.call(["service",name,"status"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
        status, needs = ("Running","N") if running else ("Not Running","Y")
        name_db = name.upper()[:20]
        with self.db.cursor() as cur:
            cur.execute("DELETE FROM Services WHERE Name=%s", (name_db,))
            cur.execute("INSERT INTO Services (Name,Status,Restart) VALUES (%s,%s,%s)", (name_db,status,needs))
        self.db.commit()
        logger.info(f"Service {name_db}: {status}")
        try:
            if use_systemctl:
                # force color via shell prefix
                cmd = f"SYSTEMD_COLORS=1 sudo systemctl status {name} --no-pager --full"
                subprocess.call(cmd, shell=True)
            else:
                cmd = ["service", name, "status"]
                subprocess.call(cmd)
        except Exception as e:
            logger.error(f"Failed to fetch detailed status: {e}")

    def control(self, name, action):
        if action not in self.VALID_ACTIONS or not self.NAME_PATTERN.match(name):
            raise ValueError("Invalid service or action")
        cmd = (["systemctl",action,name] if shutil.which("systemctl") else ["service",name,action])
        logger.info(f"Executing: {' '.join(cmd)}")
        subprocess.call(cmd)

# --- Key Reader for In-Script Reload ---

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# --- Main CLI ---
def main():
    host = input("MySQL Host [localhost]: ").strip() or "localhost"
    port = int(input("MySQL Port [3306]: ").strip() or 3306)
    user = input("MySQL User [kartik]: ").strip() or "kartik"
    password = getpass.getpass("MySQL Password: ")
    database = input("Database [KARTIK]: ").strip() or "KARTIK"

    try:
        sb = Scoreboard(host,user,password,database,port)
        with sb.db.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
    except Exception as e:
        logger.error(f"DB connection failed: {e}")
        return

    sm = ServiceManager(sb.db)
    logger.info("Ready.")

    while True:
        game = input("Which game? UNO, Chess, Carrom: ").strip()
        try:
            sb._get_table(game)
            break
        except ValueError:
            logger.error("Invalid game. Choose from UNO, Chess, Carrom.")

    while True:
        print("""
1) Add score  2) Show scores  3) Update score  4) Reset scores
5) Clear table  6) Log & clear  7) Service status  8) Control service
9) SQL prompt   0) Exit
""")
        print("> ", end="", flush=True)
        key = get_key()
        print()
        if key == '\x12':  # Ctrl+R
            print("Reloading script...")
            subprocess.call([sys.executable] + sys.argv)
            sys.exit(0)
        cmd = key
        try:
            if cmd == "0": break
            elif cmd == "1": n = input("Player name: ").strip(); s = int(input("Score: ").strip()); sb.add_score(game,n,s)
            elif cmd == "2": sb.show_scores(game)
            elif cmd == "3": n = input("Player: ").strip(); sb.update_score(game,n)
            elif cmd == "4": sb.reset_scores(game)
            elif cmd == "5": sb.clear_table(game)
            elif cmd == "6": sb.log_and_clear(game)
            elif cmd == "7": svc = input("Service: ").strip(); sm.check_service(svc)
            elif cmd == "8": svc = input("Service: ").strip(); act = input("Action (start/stop/restart/status): ").strip(); sm.control(svc,act)
            elif cmd == "9":
                conn = sb.db; conn.start_transaction(); session_log = []
                while True:
                    sql = input("SQL> ").strip()
                    if sql.lower() in ("quit","exit"): break
                    if not sql.endswith(';'): sql += ';'
                    try:
                        with conn.cursor() as c:
                            c.execute(sql)
                            if c.with_rows:
                                rows = c.fetchall(); cols = [d[0] for d in c.description]; print_table(cols,rows); session_log.append(("OK",sql,rows))
                            else:
                                logger.info(f"{c.rowcount} rows affected.")
                                session_log.append(("OK",sql,f"{c.rowcount} rows"))
                    except Exception as e:
                        logger.error(f"SQL Error: {e}")
                        session_log.append(("ERR",sql,str(e)))
                if input("Commit? [y/N]: ").strip().lower()=='y': conn.commit(); logger.info("Committed.")
                else: conn.rollback(); logger.info("Rolled back.")
                if input("Save log? [Y/n]: ").strip().lower()!='n':
                    with open('sql_session.log','w') as f:
                        for st,stmt,res in session_log: f.write(f"{st}\t{stmt}\t{res}\n")
                    logger.info("Saved sql_session.log")
                else: logger.info("Log discarded.")
            else:
                logger.error("Unknown choice")
        except Exception as e:
            logger.error(f"Operation failed: {e}")

if __name__ == "__main__":
    main()

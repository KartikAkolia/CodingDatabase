#!/usr/bin/env python3
import os
import sys
import re
import getpass
import shutil
import subprocess
import logging
import signal
import asyncio
from logging.handlers import RotatingFileHandler
from enum import Enum
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

import mysql.connector
from mysql.connector import pooling
import aiomysql
from pythonjsonlogger import jsonlogger
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.table import Table

# --- Setup console for Rich ---
console = Console()

# --- Logging Setup: Rotating and JSON-formatted ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
fh = RotatingFileHandler('game.log', maxBytes=5 * 1024 * 1024, backupCount=3)
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

# --- Enums ---
class Game(Enum):
    ALL    = 0
    UNO    = 1
    CHESS  = 2
    CARROM = 3

class ServiceAction(Enum):
    START   = 'start'
    STOP    = 'stop'
    RESTART = 'restart'
    STATUS  = 'status'

# --- Table configuration & validation ---
TABLE_MAP: Dict[Game, str] = {
    Game.UNO:    os.getenv('TABLE_UNO', 'UNO'),
    Game.CHESS:  os.getenv('TABLE_CHESS', 'CHESS'),
    Game.CARROM: os.getenv('TABLE_CARROM', 'CARROM'),
}
_table_pattern = re.compile(r'^[A-Za-z0-9_]+$')
for tbl in TABLE_MAP.values():
    if not _table_pattern.match(tbl):
        logger.error('Invalid table name in TABLE_MAP: %s', tbl)
        sys.exit(1)

# --- DB Config & Connection Pool ---
_db_pool: Optional[pooling.MySQLConnectionPool] = None
_DB_CONFIG: Dict[str, Any] = {}

def init_db_pool(host: str, port: int, user: str,
                 password: str, database: str,
                 pool_size: int = 5) -> None:
    global _db_pool, _DB_CONFIG
    _DB_CONFIG = dict(host=host, port=port, user=user,
                      password=password, db=database)
    try:
        _db_pool = pooling.MySQLConnectionPool(
            pool_name='game_pool', pool_size=pool_size,
            host=host, port=port, user=user,
            password=password, database=database
        )
        logger.info('DB pool initialized', extra={'host': host, 'db': database})
    except mysql.connector.Error as e:
        logger.error('Failed to initialize DB pool', extra={'error': str(e)})
        sys.exit(2)

@contextmanager
def get_connection():
    if _db_pool is None:
        raise RuntimeError('DB pool not initialized')
    conn = _db_pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()

# --- Utility: DB error decorator ---
def db_op(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except mysql.connector.Error as e:
            logger.error('DB error in %s', func.__name__, extra={'error': str(e)})
            sys.exit(2)
    return wrapper

# --- Helper: Rich table printing ---
def rich_print_table(columns: List[str], rows: List[tuple], title: str = "") -> None:
    table = Table(title=title, show_header=True, header_style="bold magenta")
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*(str(cell) for cell in row))
    console.print(table)

# --- Async helpers for concurrency ---
async def _async_fetch_scores(table: str) -> List[tuple]:
    pool = await aiomysql.create_pool(minsize=1, maxsize=5, **_DB_CONFIG)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT Name, Score, Code FROM `{table}`")
            rows = await cur.fetchall()
    pool.close()
    await pool.wait_closed()
    return rows

async def _async_bulk_insert(table: str, data: List[tuple]) -> int:
    pool = await aiomysql.create_pool(minsize=1, maxsize=5, **_DB_CONFIG)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.executemany(
                f"INSERT IGNORE INTO `{table}` (Name, Score, Code) VALUES (%s, %s, %s)",
                data
            )
            await conn.commit()
    pool.close()
    await pool.wait_closed()
    return len(data)

# --- Scoreboard Class ---
class Scoreboard:
    def __init__(self):
        self._player_cache: Dict[Game, List[str]] = {}

    def _get_table(self, game: Game) -> str:
        return TABLE_MAP[game]

    @db_op
    def add_score(self, game: Game, player: str, score: int) -> None:
        tbl = self._get_table(game)
        code = player[0].upper()
        q = f"INSERT IGNORE INTO `{tbl}` (Name, Score, Code) VALUES (%s, %s, %s)"
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(q, (player, score, code))
            conn.commit()
        logger.info('Added score', extra={'game': game.name, 'player': player, 'score': score})

    def show_scores(self, game: Game) -> None:
        if game == Game.ALL:
            tables = list(TABLE_MAP.values())
            results = asyncio.run(asyncio.gather(*( _async_fetch_scores(tbl) for tbl in tables )))
            for tbl_name, rows in zip(tables, results):
                if rows:
                    rich_print_table(['Name','Score','Code'], rows, title=tbl_name)
                else:
                    console.print(f"[yellow]No scores in {tbl_name}[/]")
        else:
            tbl = self._get_table(game)
            rows = asyncio.run(_async_fetch_scores(tbl))
            if rows:
                rich_print_table(['Name','Score','Code'], rows, title=tbl)
            else:
                console.print(f"[yellow]No scores in {tbl}[/]")

    @db_op
    def update_score(self, game: Game, player: str, delta: int = 1) -> None:
        tbl = self._get_table(game)
        code = player[0].upper()
        q = f"UPDATE `{tbl}` SET Score = Score + %s WHERE Code = %s"
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(q, (delta, code))
            conn.commit()
        logger.info('Updated score', extra={'game': game.name, 'player': player, 'delta': delta})

    @db_op
    def reset_scores(self, game: Game) -> None:
        tbl = self._get_table(game)
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(f"UPDATE `{tbl}` SET Score = 0")
            conn.commit()
        logger.info('Reset scores', extra={'game': game.name})

    @db_op
    def clear_table(self, game: Game) -> None:
        tbl = self._get_table(game)
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE `{tbl}`")
            conn.commit()
        logger.info('Cleared table', extra={'game': game.name})

    @db_op
    def log_and_clear(self, game: Game, log_table: str = 'Logs') -> None:
        tbl = self._get_table(game)
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(f"DELETE FROM `{log_table}` WHERE Logdate = CURDATE()")
            cur.execute(
                f"INSERT INTO `{log_table}` (Name, Score, Logdate) "
                f"SELECT Name, Score, CURDATE() FROM `{tbl}`"
            )
            cur.execute(f"UPDATE `{tbl}` SET Score = 0")
            conn.commit()
        logger.info('Logged and cleared', extra={'game': game.name})

    def get_players(self, game: Game) -> List[str]:
        if game not in self._player_cache:
            tbl = self._get_table(game)
            with get_connection() as conn, conn.cursor() as cur:
                cur.execute(f"SELECT DISTINCT Name FROM `{tbl}`")
                self._player_cache[game] = [r[0] for r in cur.fetchall()]
        return self._player_cache[game]

# --- ServiceManager Class ---
class ServiceManager:
    NAME_P = re.compile(r'^[\w\-]+$')

    @db_op
    def _record_status(self, base: str, status: str, restart: str) -> None:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM Services WHERE Name = %s", (base.upper(),))
            cur.execute(
                "INSERT INTO Services (Name, Status, Restart) VALUES (%s, %s, %s)",
                (base.upper(), status, restart)
            )
            conn.commit()

    def check_status(self, raw_name: str) -> None:
        base = raw_name[:-8] if raw_name.endswith('.service') else raw_name
        if not self.NAME_P.match(base):
            console.print(f"[red]Invalid service name: {raw_name}[/]")
            sys.exit(1)
        use_sc = shutil.which('systemctl') is not None
        cmd_chk = ['systemctl','is-active','--quiet', raw_name] if use_sc else ['service', base, 'status']
        up = subprocess.call(cmd_chk, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
        status, restart = ('Running','N') if up else ('Not Running','Y')
        self._record_status(base, status, restart)
        console.print(f"[green]{raw_name}[/]: {status}")
        cmd_det = ['systemctl','status', raw_name, '--no-pager','--full'] if use_sc else ['service', base, 'status']
        subprocess.call(cmd_det)

    def control(self, raw_name: str, action: ServiceAction) -> None:
        base = raw_name[:-8] if raw_name.endswith('.service') else raw_name
        if not self.NAME_P.match(base):
            console.print(f"[red]Invalid service name: {raw_name}[/]")
            sys.exit(1)
        use_sc = shutil.which('systemctl') is not None
        cmd = ['systemctl', action.value, raw_name] if use_sc else ['service', base, action.value]
        subprocess.call(cmd)

# --- Fetch and cache services once ---
def get_service_names() -> List[str]:
    try:
        out = subprocess.check_output(
            ['systemctl','list-unit-files','--type=service','--no-legend'],
            text=True
        )
        return [line.split()[0] for line in out.splitlines() if line]
    except Exception:
        return []

# --- SQL Prompt Helper ---
def sql_prompt_loop() -> None:
    assert _db_pool is not None, "DB pool not initialized"
    conn = _db_pool.get_connection()
    cursor = conn.cursor()
    prompt = PromptSession('SQL> ')
    try:
        while True:
            try:
                stmt = prompt.prompt().strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if stmt.lower() in ('exit', 'quit', '\\q'):
                break
            if not stmt.endswith(';'):
                stmt += ';'
            try:
                cursor.execute(stmt)
                if cursor.with_rows:
                    rows = cursor.fetchall()
                    cols = [d[0] for d in cursor.description]
                    rich_print_table(cols, rows, title="Query Result")
                else:
                    console.print(f"[yellow]{cursor.rowcount} rows affected.[/]")
            except Exception as e:
                console.print(f"[red]SQL Error:[/] {e}")
    finally:
        choice = PromptSession().prompt('Commit this session? [y/N]: ').strip().lower()
        if choice == 'y':
            conn.commit()
        else:
            conn.rollback()
        cursor.close()
        conn.close()

# --- Graceful Shutdown ---
def shutdown_handler(signum: int, frame: Any) -> None:
    logger.info(f"Received signal {signum}, shutting down.")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

# --- Main and Menu Setup ---
def main() -> None:
    session = PromptSession()
    games = [g.name for g in Game]
    service_names = get_service_names()
    MENU = [
        ('1','Add score'),
        ('2','Show scores'),
        ('3','Update score'),
        ('4','Reset scores'),
        ('5','Clear table'),
        ('6','Log & clear'),
        ('7','Service status'),
        ('8','Control service'),
        ('9','SQL prompt'),
        ('0','Exit'),
    ]
    games_completer   = WordCompleter(games, ignore_case=True)
    service_completer = WordCompleter(service_names, ignore_case=True)
    menu_completer    = WordCompleter([o for o,_ in MENU], ignore_case=True)

    # DB config
    host = os.getenv('DB_HOST') or session.prompt('DB Host [localhost]: ') or 'localhost'
    port_str = os.getenv('DB_PORT') or session.prompt('DB Port [3306]: ') or '3306'
    try:
        port = int(port_str)
    except ValueError:
        console.print("[red]Invalid port.[/]")
        sys.exit(1)
    user = os.getenv('DB_USER') or session.prompt('DB User [kartik]: ') or 'kartik'
    pwd  = os.getenv('DB_PASSWORD') or getpass.getpass('DB Password: ')
    db   = os.getenv('DB_NAME') or session.prompt('Database [KARTIK]: ') or 'KARTIK'
    init_db_pool(host, port, user, pwd, db)

    sb = Scoreboard()
    sm = ServiceManager()

    # Choose game
    while True:
        g = session.prompt('Choose game (ALL, UNO, CHESS, CARROM): ',
                           completer=games_completer).upper()
        if g in Game.__members__:
            game = Game[g]
            break
        console.print("[red]Invalid game.[/]")

    # Action functions
    def add_action():
        if game == Game.ALL:
            console.print("[red]Cannot add score to ALL.[/]")
            return
        n = session.prompt('Player name: ')
        s = session.prompt('Score: ')
        sb.add_score(game, n.strip(), int(s.strip()))

    def show_action(): sb.show_scores(game)

    def update_action():
        if game == Game.ALL:
            console.print("[red]Cannot update score in ALL.[/]")
            return
        players = sb.get_players(game)
        name = session.prompt('Player: ',
                              completer=WordCompleter(players, ignore_case=True))
        sb.update_score(game, name.strip())

    def reset_action():
        if game == Game.ALL:
            console.print("[red]Cannot reset ALL.[/]")
            return
        sb.reset_scores(game)

    def clear_action():
        if game == Game.ALL:
            console.print("[red]Cannot clear ALL.[/]")
            return
        sb.clear_table(game)

    def log_clear_action():
        if game == Game.ALL:
            console.print("[red]Cannot log & clear ALL.[/]")
            return
        sb.log_and_clear(game)

    def status_action():
        svc = session.prompt('Service: ', completer=service_completer)
        sm.check_status(svc.strip())

    def control_action():
        svc = session.prompt('Service: ', completer=service_completer)
        act = session.prompt(
            'Action (START/STOP/RESTART/STATUS): ',
            completer=WordCompleter([a.name for a in ServiceAction], ignore_case=True)
        )
        sm.control(svc.strip(), ServiceAction[act.upper()])

    def sql_action(): sql_prompt_loop()
    def exit_action(): sys.exit(0)

    dispatch: Dict[str, Callable[[], None]] = {
        '1': add_action,
        '2': show_action,
        '3': update_action,
        '4': reset_action,
        '5': clear_action,
        '6': log_clear_action,
        '7': status_action,
        '8': control_action,
        '9': sql_action,
        '0': exit_action,
    }

    def print_menu():
        rich_print_table(['Option','Action'], MENU, title="Main Menu")

    # Main loop
    while True:
        print_menu()
        choice = session.prompt('> ', completer=menu_completer).strip()
        action = dispatch.get(choice)
        if action:
            try:
                action()
            except Exception as e:
                logger.error('Operation failed', extra={'error': str(e)})
                sys.exit(1)
        else:
            console.print("[red]Invalid choice[/]")

if __name__ == '__main__':
    main()

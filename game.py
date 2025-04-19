import os
import subprocess
import shutil
import mysql.connector
import getpass

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
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        self.use_inventory = use_inventory

    def _get_table(self, game: str) -> str:
        if self.use_inventory:
            tbl = self._lookup_inventory(game)
            if tbl:
                return tbl
        if game in self.GAME_ID:
            return game
        raise ValueError(f"Unknown game: {game!r}")

    def _lookup_inventory(self, game: str) -> str | None:
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT NAME FROM Inventory WHERE ID = %s",
                (self.GAME_ID.get(game),)
            )
            row = cur.fetchone()
        return row[0] if row else None

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

    def reset_scores(self, game: str) -> None:
        tbl = self._get_table(game)
        with self.db.cursor() as cur:
            cur.execute(f"UPDATE `{tbl}` SET Score = 0")
        self.db.commit()
        print(f"All scores reset in {tbl}")

    def clear_table(self, game: str) -> None:
        tbl = self._get_table(game)
        with self.db.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE `{tbl}`")
        self.db.commit()
        print(f"All records deleted from {tbl}")

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

    @staticmethod
    def _is_running(name: str) -> bool:
        try:
            return subprocess.call(
                ["systemctl", "is-active", "--quiet", name]
            ) == 0
        except FileNotFoundError:
            return subprocess.call(
                ["service", name, "status"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            ) == 0

    def check_service(self, name: str) -> None:
        running = self._is_running(name)
        status_str    = "Running" if running else "Not Running"
        needs_restart = "N"       if running else "Y"
        name_db       = name.upper()[:20]

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

        # Prefer systemctl, fall back to service
        if shutil.which("systemctl"):
            cmd = ["systemctl", action, name]
        else:
            cmd = ["service", name, action]

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

    sb = Scoreboard(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )
    sm = ServiceManager(sb.db)

    game = input("Which game? UNO, Chess, Carrom: ").strip()

    while True:
        print("""
1) Add score   2) Show scores   3) Update score   4) Reset scores
5) Clear table 6) Log & clear   7) Service status   8) Control service
0) Exit
""")
        cmd = input("> ").strip()

        if cmd == "0":
            break
        elif cmd == "1":
            name  = input("Player name: ").strip()
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
            svc = input("Which service would you like to check? ").strip()
            sm.check_service(svc)
        elif cmd == "8":
            svc    = input("Service name: ").strip()
            action = input("Action (start/stop/restart/status): ").strip()
            sm.control(svc, action)
        else:
            print("Unknown choice.")

if __name__ == "__main__":
    main()

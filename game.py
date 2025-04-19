import os
import subprocess
import mysql.connector
from typing import Optional

class Scoreboard:
    GAME_ID = {
        "UNO":   1,
        "Chess": 2,
        "Carrom":3,
    }

    def __init__(self,
                 user: str = "kartik",
                 password: str = "Kartik84",
                 host: str = "192.168.0.224",
                 database: str = "KARTIK",
                 port: int = 3306):
        self.db = mysql.connector.connect(
            host=host, user=user, password=password, database=database, port=port
        )

    def _get_table(self, game: str) -> str:
        """Look up the table name for a game via the Inventory table."""
        game_id = self.GAME_ID.get(game)
        if game_id is None:
            raise ValueError(f"Unknown game: {game!r}")
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT NAME FROM Inventory WHERE ID = %s",
                (game_id,)
            )
            row = cur.fetchone()
            if not row:
                raise LookupError(f"No inventory entry for game {game}")
            return row[0]

    def add_score(self, game: str, player_name: str, score: int) -> None:
        tbl = self._get_table(game)
        code = player_name[0]
        with self.db.cursor() as cur:
            # check existence
            cur.execute(
                f"SELECT COUNT(*) FROM `{tbl}` WHERE code = %s",
                (code,)
            )
            (count,) = cur.fetchone()
            if count:
                print("Record already exists for code", code)
            else:
                cur.execute(
                    f"INSERT INTO `{tbl}` (name, score, code) VALUES (%s, %s, %s)",
                    (player_name, score, code)
                )
                self.db.commit()
                print("Inserted", player_name, score)

    def show_scores(self, game: str) -> None:
        tbl = self._get_table(game)
        with self.db.cursor() as cur:
            cur.execute(f"SELECT name, score, code FROM `{tbl}`")
            for name, score, code in cur:
                print(f"{name:<10} {score:>4}   code={code}")

    def update_score(self, game: str, player_name: str, delta: int = 1) -> None:
        tbl = self._get_table(game)
        code = player_name[0]
        with self.db.cursor() as cur:
            cur.execute(
                f"UPDATE `{tbl}` SET score = score + %s WHERE code = %s",
                (delta, code)
            )
            self.db.commit()
            print(f"Updated code {code} by {delta}")

    def reset_scores(self, game: str) -> None:
        tbl = self._get_table(game)
        with self.db.cursor() as cur:
            cur.execute(f"UPDATE `{tbl}` SET score = 0")
            self.db.commit()
            print(f"All scores reset in {tbl}")

    def clear_table(self, game: str) -> None:
        tbl = self._get_table(game)
        with self.db.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE `{tbl}`")
            self.db.commit()
            print(f"All records deleted from {tbl}")

    def log_and_clear(self, game: str, log_table: str = "Logs") -> None:
        """Archive today's scores to Logs and zero out the game table."""
        tbl = self._get_table(game)
        today = "CURDATE()"  # let SQL handle it
        with self.db.cursor() as cur:
            # remove old logs for today
            cur.execute(f"DELETE FROM `{log_table}` WHERE logdate = {today}")
            # insert new logs
            cur.execute(
                f"INSERT INTO `{log_table}` (name, score, logdate) "
                f"SELECT name, score, {today} FROM `{tbl}`"
            )
            # zero out
            cur.execute(f"UPDATE `{tbl}` SET score = 0")
            self.db.commit()
            print(f"Logged and cleared scores for {game}")

class ServiceManager:
    SERVICES = ["ssh", "apache2", "mysql"]

    def __init__(self, db_conn: mysql.connector.MySQLConnection):
        self.db = db_conn

    def check_all(self) -> None:
        """Check each service, record its status in Services table."""
        with self.db.cursor() as cur:
            cur.execute("TRUNCATE TABLE Services")
            self.db.commit()

        for svc in self.SERVICES:
            status = self._is_running(svc)
            with self.db.cursor() as cur:
                cur.execute(
                    "INSERT INTO Services (Name, Status, NeedsAttention) "
                    "VALUES (%s, %s, %s)",
                    (svc.upper(),
                     "Running" if status else "Not Running",
                     "N" if status else "Y")
                )
                self.db.commit()
            print(f"{svc}: {'✓ running' if status else '✗ stopped'}")

    @staticmethod
    def _is_running(name: str) -> bool:
        """Return True if service is running (exit code 0)."""
        return subprocess.call(
            ["/etc/init.d/" + name, "status"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        ) == 0

    def show_status(self) -> None:
        with self.db.cursor() as cur:
            cur.execute("SELECT Name, Status FROM Services")
            for name, status in cur:
                print(f"{name}: {status}")

    def control(self, name: str, action: str) -> None:
        """Start, stop, or restart a service."""
        if action not in ("start", "stop", "restart", "status"):
            raise ValueError(action)
        cmd = ["/etc/init.d/" + name, action]
        print(" ".join(cmd))
        subprocess.call(cmd)

# ———————— CLI loop (separate from business logic) ————————

def main():
    sb = Scoreboard()
    sm = ServiceManager(sb.db)

    game = input("Which game? UNO, Chess, Carrom: ").strip()
    while True:
        print("""
1) Add score   2) Show scores   3) Update score   4) Reset scores
5) Clear table 6) Log & clear   7) Service status  8) Show service table
9) Control service   0) Exit""")
        cmd = input("> ").strip()

        if cmd == "0":
            break
        elif cmd == "1":
            name = input("Player name: ")
            score = int(input("Score: "))
            sb.add_score(game, name, score)
        elif cmd == "2":
            sb.show_scores(game)
        elif cmd == "3":
            name = input("Player name: ")
            sb.update_score(game, name)
        elif cmd == "4":
            sb.reset_scores(game)
        elif cmd == "5":
            sb.clear_table(game)
        elif cmd == "6":
            sb.log_and_clear(game)
        elif cmd == "7":
            sm.check_all()
        elif cmd == "8":
            sm.show_status()
        elif cmd == "9":
            svc = input("Service name: ").strip()
            act = input("Action (start/stop/restart/status): ").strip()
            sm.control(svc, act)
        else:
            print("Unknown choice.")

if __name__ == "__main__":
    main()

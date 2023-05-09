#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
import sqlite3
from pathlib import Path
import argparse
import typing as t


def create_db(database_path: Path) -> None:
    """
    Создать базу данных
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Создать таблицу с информацией о пункте назначения
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS destination (
            number INTEGER PRIMARY KEY,
            dest TEXT NOT NULL
        )
        """
    )

    # Создать таблицу с информацией о времени отправления
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS time (
            departure_time TEXT NOT NULL,
            number INTEGER NOT NULL,
            FOREIGN KEY(number) REFERENCES destination(number)
        )
        """
    )
    conn.close()


def display_workers(staff: t.List[t.Dict[str, t.Any]]) -> None:
    """
    Отобразить список работников.
    """
    # Проверить, что список работников не пуст.
    if staff:
        # Заголовок таблицы.
        line = "+-{}-+-{}-+-{}-+".format("-" * 30, "-" * 20, "-" * 20)
        print(line)
        print(
            "|{:^30} | {:^20} | {:^20} |".format(
                "Пункт назначения", "Номер поезда", "Время отправления"
            )
        )
        print(line)

        # Вывести данные о всех сотрудниках
        for idx, user in enumerate(staff, 1):
            print(
                "| {:<30} | {:<20} | {:>20} |".format(
                    user.get("dest", ""),
                    user.get(
                        "number",
                    ),
                    user.get("departure_time", ""),
                )
            )
            print(line)
    else:
        print("Список работников пуст.")


def add_worker(
    database_path: Path, dest: str, number: int, departure_time: str
) -> None:
    """
    Добавить работника в базу данных
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Получить идентификатор маршрута в базе данных
    # Если такой записи нет, то добавить информацию о новом маршруте
    cursor.execute(
        """
        SELECT number FROM destination WHERE dest = ?
        """,
        (dest,),
    )
    row = cursor.fetchone()
    if row is None:
        cursor.execute(
            """
            INSERT INTO destination (dest) VALUES (?)
            """,
            (dest,),
        )
        number = cursor.lastrowid

    else:
        number = row[0]

    # Добавить информацию о новом маршруте
    cursor.execute(
        """
        INSERT INTO time (number, departure_time)
        VALUES (?, ?)
        """,
        (number, departure_time),
    )
    conn.commit()
    conn.close()


def select_all(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать всех работников.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT destination.dest, time.departure_time, destination.number
        FROM destination
        INNER JOIN time ON time.number = destination.number
        """
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "dest": row[0],
            "departure_time": row[1],
            "number": row[2],
        }
        for row in rows
    ]


def select_by_period(database_path: Path, pnumber: int) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать всех пользователей с заданным номером телефона.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT destination.dest, time.departure_time, destination.number
        FROM destination
        INNER JOIN time ON time.number = destination.number
        WHERE destination.number == ?
        """,
        (pnumber,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "dest": row[0],
            "departure_time": row[1],
            "number": row[2],
        }
        for row in rows
    ]


def main(command_line=None):
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.home() / "routes.db"),
        help="The database file name",
    )

    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("workers")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    subparsers = parser.add_subparsers(dest="command")

    # Создать субпарсер для добавления пользователей.
    add = subparsers.add_parser("add", parents=[file_parser], help="Add a new worker")
    add.add_argument(
        "-n",
        "--number",
        action="store",
        type=int,
        required=True,
        help="The train number",
    )

    add.add_argument("-d", "--destination", action="store", help="Destination")
    add.add_argument(
        "-t", "--time", action="store", required=True, help="Departure time"
    )

    # Создать субпарсер для отображения всех пользователей.
    _ = subparsers.add_parser(
        "display", parents=[file_parser], help="Display all workers"
    )

    # Создать субпарсер для выбора пользователей.
    select = subparsers.add_parser(
        "select", parents=[file_parser], help="Select the workers"
    )
    select.add_argument(
        "-N",
        "--number",
        action="store",
        type=int,
        required=True,
        help="The required phone number",
    )

    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)

    # Получить путь к файлу базы данных.
    db_path = Path(args.db)
    create_db(db_path)

    # Добавить пользователей.
    if args.command == "add":
        add_worker(db_path, args.destination, args.number, args.time)

    # Отобразить всех рпользователей.
    elif args.command == "display":
        display_workers(select_all(db_path))

    # Выбрать требуемых пользователей.
    elif args.command == "select":
        display_workers(select_by_period(db_path, args.number))
        pass


if __name__ == "__main__":
    main()

"""Создание таблиц базы данных истории команд"""
import sqlite3


def create_tables(db_name: str) -> None:
    """
    Создание БД, состоящей из трех таблиц requests, hotels, request_results
    :param db_name: имя файла БД
    :return:
    """
    try:
        connection = sqlite3.connect(db_name, timeout=20)
        cursor = connection.cursor()

        create_tables_query = """
        CREATE TABLE IF NOT EXISTS requests (
            requestId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            userId INTEGER NOT NULL,
            command TEXT,
            requestDate datetime,
            destination TEXT);

        CREATE TABLE IF NOT EXISTS request_results (
            resultId INTEGER PRIMARY KEY AUTOINCREMENT,
            requestId INTEGER,
            hotelId INTEGER,        
            FOREIGN KEY (requestId)
                REFERENCES requests (requestId),
            FOREIGN KEY (hotelId)
                REFERENCES hotels (hotelId));

        CREATE TABLE IF NOT EXISTS hotels (
            hotelId INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            link TEXT,
            UNIQUE (name, link));"""

        cursor.executescript(create_tables_query)
        connection.commit()

        cursor.close()
    except sqlite3.Error as error:
        if connection:
            connection.rollback()
        print("Ошибка при создании БД sqlite", error)
    finally:
        if connection:
            connection.close()

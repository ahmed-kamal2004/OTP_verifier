import os
import smtplib
import psycopg2
from psycopg2.extras import RealDictCursor
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import random


class Constant:
    class DataBaseInteraction:
        database = "fastApi"
        user = "postgres"
        password = "9341"
        cursor = None
        conn = None

        def __init__(self):
            pass

        @staticmethod
        def connect():
            try:
                Constant.DataBaseInteraction.conn = psycopg2.connect(
                    host="localhost",
                    database=Constant.DataBaseInteraction.database,
                    user=Constant.DataBaseInteraction.user,
                    password=Constant.DataBaseInteraction.password,
                    cursor_factory=RealDictCursor,
                )
                Constant.DataBaseInteraction.cursor = (
                    Constant.DataBaseInteraction.conn.cursor()
                )

                Constant.DataBaseInteraction.cursor.execute(
                    """CREATE TABLE IF NOT EXISTS emails (
                               id SERIAL PRIMARY KEY,
                               email varchar NOT NULL UNIQUE
                )"""
                )
                Constant.DataBaseInteraction.conn.commit()

            except Exception as e:
                print(f"{e}")
                raise e

        @staticmethod
        def add_email(email: str):
            if (
                not Constant.DataBaseInteraction.conn
                or not Constant.DataBaseInteraction.cursor
            ):
                Constant.DataBaseInteraction.connect()
            Constant.DataBaseInteraction.conn.rollback()

            Constant.DataBaseInteraction.cursor.execute(
                """INSERT INTO emails (email) VALUES(%s);""", (email,)
            )
            Constant.DataBaseInteraction.cursor.fetchall()
            Constant.DataBaseInteraction.conn.commit()

        @staticmethod
        def verify_email(email: str) -> bool:
            if (
                not Constant.DataBaseInteraction.conn
                or not Constant.DataBaseInteraction.cursor
            ):
                Constant.DataBaseInteraction.connect()
            Constant.DataBaseInteraction.conn.rollback()
            Constant.DataBaseInteraction.cursor.execute(
                """SELECT id FROM emails WHERE email = %s;""", (email,)
            )
            found = Constant.DataBaseInteraction.cursor.fetchone()
            if found:
                return True
            return False

    class EmailInteraction:
        subject = "OTP vertification"
        sender_email = None
        sender_password = None
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        @staticmethod
        def static_constructor(sender_email, sender_password):
            Constant.EmailInteraction.sender_email = sender_email
            Constant.EmailInteraction.sender_password = sender_password

        @staticmethod
        def send(message: str, receiver) -> bool:
            msg = MIMEMultipart()
            msg["From"] = Constant.EmailInteraction.sender_email
            msg["To"] = receiver
            msg["Subject"] = Constant.EmailInteraction.subject
            msg.attach(MIMEText(message, "plain"))
            with smtplib.SMTP(
                Constant.EmailInteraction.smtp_server,
                Constant.EmailInteraction.smtp_port,
            ) as server:
                server.starttls()
                server.login(
                    Constant.EmailInteraction.sender_email,
                    Constant.EmailInteraction.sender_password,
                )
                server.sendmail(
                    Constant.EmailInteraction.sender_email, receiver, msg.as_string()
                )

    class ConsoleInteraction:
        @staticmethod
        def print_and_get(msg: str, *choices) -> str:
            print(msg)
            for one in choices:
                print(one)
            data = input().strip().capitalize()
            return data

        @staticmethod
        def print_only(msg: str):
            print(msg.strip().capitalize())


class MainProgram:
    time = None
    OTP = None

    @staticmethod
    def run():
        Constant.ConsoleInteraction.print_only("Welcome is vertofication Page")
        Constant.EmailInteraction.static_constructor(
            "ahmedkamal200427@gmail.com", "dagq bfte sfgp gmjk"
        )  ## One time password
        while True:
            choice = int(
                Constant.ConsoleInteraction.print_and_get(
                    "Enter your choice :", "Sign Up", "Log in", "Exit"
                )
            )
            if choice == 1:
                ## Adding the email to the database

                email = Constant.ConsoleInteraction.print_and_get(
                    "Enter your email address: "
                )
                try:
                    Constant.DataBaseInteraction.add_email(email)
                except Exception as e:
                    Constant.ConsoleInteraction.print_only("Email already exists")
                else:
                    Constant.ConsoleInteraction.print_only("signed up successfully")


            elif choice == 2:
                email = Constant.ConsoleInteraction.print_and_get(
                    "Enter your email address: "
                )
                if Constant.DataBaseInteraction.verify_email(email) == True:
                    while True:
                        MainProgram.genearate_otp()
                        try:
                            Constant.EmailInteraction.send(str(MainProgram.OTP), email)
                        except Exception as error:
                            print(error)
                            break
                        else:
                            Constant.ConsoleInteraction.print_only("Check your gmail")
                            OTP = Constant.ConsoleInteraction.print_and_get(
                                "Enter your OTP: "
                            )
                            if MainProgram.verify_otp(OTP) == True:
                                Constant.ConsoleInteraction.print_only(
                                    "Logged in successfully"
                                )
                                break
                            else:
                                Constant.ConsoleInteraction.print_only(
                                    "Wrong OTP or expired"
                                )
                else:
                    Constant.ConsoleInteraction.print_only("Sign up First")

            else:
                break
        Constant.ConsoleInteraction.print_only("Thanks for using my app")

    @classmethod
    def genearate_otp(cls):
        cls.OTP = random.randint(100000, 999999)
        cls.time = datetime.datetime.now()

    @classmethod
    def verify_otp(cls,OTP:int):
        if cls.time + datetime.timedelta(minutes=5) < datetime.datetime.now():
            print(cls.time + datetime.timedelta(minutes=5))
            return False
        if str(OTP) != str(cls.OTP):
            print(cls.OTP)
            return False
        return True


if __name__ == "__main__":
    MainProgram.run()

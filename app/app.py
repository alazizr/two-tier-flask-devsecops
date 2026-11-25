import logging
import os
import time
from flask import Flask, jsonify, render_template
import mysql.connector
from mysql.connector import Error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")


def get_db_connection(retries=5, delay=2):
    db_host = os.getenv("MYSQL_HOST")
    db_user = os.getenv("MYSQL_USER")
    db_password = os.getenv("MYSQL_PASSWORD")
    db_name = os.getenv("MYSQL_DB", "devops")

    if not all([db_host, db_user, db_password]):
        logger.error("Missing required database environment variables.")
        return None

    for attempt in range(1, retries + 1):
        try:
            return mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name,
                connection_timeout=5,
            )
        except Error as err:
            logger.warning("DB connection attempt %d failed: %s", attempt, err)
            time.sleep(delay)

    return None


@app.route("/health")
def health():
    conn = get_db_connection(retries=1, delay=0)
    if conn is None:
        return jsonify({"status": "unhealthy", "database": "disconnected", "version": APP_VERSION}), 503
    conn.close()
    return jsonify({"status": "healthy", "database": "connected", "version": APP_VERSION}), 200


@app.route("/")
def home():
    conn = get_db_connection()
    if conn is None:
        return "Database Connection Failed", 503

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, message, created_at FROM messages ORDER BY id DESC")
        messages = cursor.fetchall()
        cursor.close()
        return render_template("index.html", messages=messages)
    except Error as err:
        logger.error("Query failed: %s", err)
        return "Internal Database Error", 500
    finally:
        conn.close()


@app.route("/api/messages")
def api_messages():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database Connection Failed"}), 503

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, message, created_at FROM messages ORDER BY id DESC")
        data = cursor.fetchall()
        cursor.close()
        return jsonify({"version": APP_VERSION, "data": data}), 200
    except Error as err:
        logger.error("API query failed: %s", err)
        return jsonify({"error": "Internal Database Error"}), 500
    finally:
        conn.close()

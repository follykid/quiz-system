from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

import sqlite3

from models.database import get_db_connection
import services.state as state

admin_bp = Blueprint("admin", __name__)


# =========================
# 老師首頁
# =========================
@admin_bp.route("/")
def index():

    conn = get_db_connection()

    teams = conn.execute(
        "SELECT * FROM teams ORDER BY id ASC"
    ).fetchall()

    pending_orders = conn.execute("""
        SELECT
            purchase_logs.id as log_id,
            users.username,
            items.name as item_name
        FROM purchase_logs
        JOIN users
            ON purchase_logs.user_id = users.id
        JOIN items
            ON purchase_logs.item_id = items.id
        WHERE purchase_logs.status='pending'
        AND items.name!='銘謝惠顧'
        ORDER BY purchase_logs.purchase_time DESC
    """).fetchall()

    conn.close()

    grouped_orders = {}

    for order in pending_orders:

        username = order["username"]

        if username not in grouped_orders:
            grouped_orders[username] = []

        grouped_orders[username].append({
            "log_id": order["log_id"],
            "item_name": order["item_name"]
        })

    return render_template(
        "index.html",
        teams=teams,
        grouped_orders=grouped_orders
    )


# =========================
# 新增學生
# =========================
@admin_bp.route("/add_team", methods=["POST"])
def add_team():

    team_name = request.form.get("name")

    if team_name:

        try:

            conn = get_db_connection()

            conn.execute(
                "INSERT INTO teams (name, score) VALUES (?, 0)",
                (team_name,)
            )

            conn.execute(
                """
                INSERT INTO users
                (username, password, team_name)
                VALUES (?, '1234', ?)
                """,
                (team_name, team_name)
            )

            conn.commit()
            conn.close()

            state.DISPLAY_NEEDS_UPDATE = True

        except sqlite3.IntegrityError:
            pass

    return redirect(url_for("admin.index"))


# =========================
# 加分 / 扣分
# =========================
@admin_bp.route("/update/<name>/<delta>")
def update_score(name, delta):

    try:

        val = int(delta)

        conn = get_db_connection()

        conn.execute(
            """
            UPDATE teams
            SET score = score + ?
            WHERE name = ?
            """,
            (val, name)
        )

        conn.commit()
        conn.close()

        state.DISPLAY_NEEDS_UPDATE = True

    except:
        pass

    return redirect(url_for("admin.index"))


# =========================
# 刪除學生
# =========================
@admin_bp.route("/delete_team/<name>")
def delete_team(name):

    conn = get_db_connection()

    user = conn.execute(
        "SELECT id FROM users WHERE username = ?",
        (name,)
    ).fetchone()

    if user:

        conn.execute(
            "DELETE FROM purchase_logs WHERE user_id = ?",
            (user["id"],)
        )

        conn.execute(
            "DELETE FROM users WHERE id = ?",
            (user["id"],)
        )

    conn.execute(
        "DELETE FROM teams WHERE name = ?",
        (name,)
    )

    conn.commit()
    conn.close()

    state.DISPLAY_NEEDS_UPDATE = True

    return redirect(url_for("admin.index"))
# =========================
# 核銷寶物
# =========================
@admin_bp.route("/redeem/<int:log_id>")
def redeem_item(log_id):

    conn = get_db_connection()

    conn.execute(
        """
        UPDATE purchase_logs
        SET status='used'
        WHERE id=?
        """,
        (log_id,)
    )

    conn.commit()
    conn.close()

    state.DISPLAY_NEEDS_UPDATE = True

    return redirect(url_for("admin.index"))


# =========================
# 強制更新排行榜
# =========================
@admin_bp.route("/trigger_update")
def trigger_update():

    state.DISPLAY_NEEDS_UPDATE = True

    return redirect(url_for("admin.index"))
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

import random

from models.database import get_db_connection
import services.state as state

student_bp = Blueprint("student", __name__)


# =========================
# 學生登入 / 背包
# =========================
@student_bp.route("/student", methods=["GET", "POST"])
def student():

    msg = ""

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE username=?
            AND password=?
            """,
            (username, password)
        ).fetchone()

        conn.close()

        if user:

            session["user"] = user["username"]

            return redirect(
                url_for("student.student")
            )

        else:

            msg = "❌ 帳號或密碼錯誤！"

    if "user" in session:

        conn = get_db_connection()

        user_info = conn.execute(
            """
            SELECT *
            FROM users
            WHERE username=?
            """,
            (session["user"],)
        ).fetchone()

        team_info = conn.execute(
            """
            SELECT *
            FROM teams
            WHERE name=?
            """,
            (user_info["team_name"],)
        ).fetchone()

        items = conn.execute(
            "SELECT * FROM items"
        ).fetchall()

        my_items = conn.execute("""
            SELECT
                items.name,
                items.description,
                purchase_logs.status
            FROM purchase_logs
            JOIN items
            ON purchase_logs.item_id = items.id
            WHERE purchase_logs.user_id=?
            ORDER BY
            purchase_logs.status DESC,
            purchase_logs.purchase_time DESC
        """,
        (user_info["id"],)
        ).fetchall()

        conn.close()

        return render_template(
            "student.html",
            user=user_info,
            team=team_info,
            items=items,
            my_items=my_items,
            msg=msg
        )

    return render_template(
        "student.html",
        user=None,
        msg=msg
    )


# =========================
# 抽獎
# =========================
@student_bp.route("/draw")
def draw_item():

    if "user" not in session:

        return redirect(
            url_for("student.student")
        )

    DRAW_COST = 20

    conn = get_db_connection()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE username=?
        """,
        (session["user"],)
    ).fetchone()

    team = conn.execute(
        """
        SELECT *
        FROM teams
        WHERE name=?
        """,
        (user["team_name"],)
    ).fetchone()

    if team and team["score"] >= DRAW_COST:

        conn.execute(
            """
            UPDATE teams
            SET score = score - ?
            WHERE name = ?
            """,
            (DRAW_COST, team["name"])
        )

        all_items = conn.execute(
            "SELECT * FROM items"
        ).fetchall()

        items_list = list(all_items)

        weights = [
            item["weight"]
            for item in items_list
        ]

        chosen_item = random.choices(
            items_list,
            weights=weights,
            k=1
        )[0]

        conn.execute(
            """
            INSERT INTO purchase_logs
            (user_id,item_id,status)
            VALUES (?,?,'pending')
            """,
            (
                user["id"],
                chosen_item["id"]
            )
        )

        conn.commit()

        state.DISPLAY_NEEDS_UPDATE = True

        if chosen_item["name"] == "銘謝惠顧":

            msg = (
                "😢 噢不！你抽中了【銘謝惠顧】"
                "，扣除20分，下次再試試！"
            )

        else:

            msg = (
                f"🎉 恭喜抽中："
                f"【{chosen_item['name']}】"
                "，已放入背包！"
            )

    else:

        msg = (
            f"❌ 點數不足 "
            f"{DRAW_COST} 分"
        )

    conn.close()

    return f"""
    <script>
        alert('{msg}');
        window.location.href='/student';
    </script>
    """


# =========================
# 登出
# =========================
@student_bp.route("/logout")
def logout():

    session.pop("user", None)

    return redirect(
        url_for("student.student")
    )
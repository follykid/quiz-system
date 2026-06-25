from flask import Blueprint, render_template, jsonify, request

from models.database import get_db_connection
import services.state as state

display_bp = Blueprint("display", __name__)


# =========================
# 大螢幕排行榜
# =========================
@display_bp.route("/display")
def display():

    conn = get_db_connection()

    teams = conn.execute(
        """
        SELECT *
        FROM teams
        ORDER BY score DESC, id ASC
        """
    ).fetchall()

    pending_orders = conn.execute("""
        SELECT
            users.username,
            items.name as item_name
        FROM purchase_logs
        JOIN users
            ON purchase_logs.user_id = users.id
        JOIN items
            ON purchase_logs.item_id = items.id
        WHERE purchase_logs.status='pending'
        AND items.name!='銘謝惠顧'
    """).fetchall()

    conn.close()

    team_items = {}

    for order in pending_orders:

        username = order["username"]

        if username not in team_items:
            team_items[username] = []

        team_items[username].append(
            order["item_name"]
        )

    return render_template(
        "display.html",
        teams=teams,
        team_items=team_items
    )


# =========================
# 排行榜 API
# =========================
@display_bp.route("/api/scores")
def get_scores():

    force = request.args.get(
        "force",
        "false"
    ) == "true"

    if not force and not state.DISPLAY_NEEDS_UPDATE:
        return jsonify({
            "status": "no_change"
        })

    if not force:
        state.DISPLAY_NEEDS_UPDATE = False

    conn = get_db_connection()

    teams = conn.execute("""
        SELECT
            name,
            score
        FROM teams
        ORDER BY score DESC, id ASC
    """).fetchall()

    pending_orders = conn.execute("""
        SELECT
            users.username,
            items.name as item_name
        FROM purchase_logs
        JOIN users
            ON purchase_logs.user_id = users.id
        JOIN items
            ON purchase_logs.item_id = items.id
        WHERE purchase_logs.status='pending'
        AND items.name!='銘謝惠顧'
    """).fetchall()

    conn.close()

    team_items = {}

    for order in pending_orders:

        username = order["username"]

        if username not in team_items:
            team_items[username] = []

        team_items[username].append(
            order["item_name"]
        )

    team_list = []

    for team in teams:

        team_list.append({
            "name": team["name"],
            "score": team["score"],
            "items": team_items.get(
                team["name"],
                []
            )
        })

    return jsonify({
        "status": "update",
        "teams": team_list
    })
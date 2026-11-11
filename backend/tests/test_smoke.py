from app import create_app
from models import db


def test_health_and_schema():
    app = create_app("sqlite://")
    assert app.test_client().get("/api/health").json == {"status": "ok"}
    with app.app_context():
        tables = set(db.inspect(db.engine).get_table_names())
    assert tables == {"users", "households", "memberships", "expenses",
                      "expense_shares", "settlements", "chores"}

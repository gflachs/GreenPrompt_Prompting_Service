import pytest
from app.controllers.db_controller import DatabaseController

@pytest.fixture
def db_instance(tmp_path):
    """Fixture for creating a DatabaseController instance with a temporary SQLite database."""
    db_path = tmp_path / "test.db"
    db_controller = DatabaseController.get_instance(str(db_path))
    yield db_controller
    db_controller.reset_database()  # Clean up after test

def test_create_table(db_instance):
    """Test table creation."""
    db_instance.create_table("test_table", [
        ("id", "INTEGER PRIMARY KEY"),
        ("name", "TEXT"),
        ("age", "INTEGER")
    ])
    tables = db_instance.return_custom_query(
        "SELECT name FROM sqlite_master WHERE type='table';"
    )
    assert any(table["name"] == "test_table" for table in tables)

def test_insert_and_fetch_data(db_instance):
    """Test inserting and fetching data."""
    db_instance.create_table("test_table", [
        ("id", "INTEGER PRIMARY KEY"),
        ("name", "TEXT"),
        ("age", "INTEGER")
    ])
    data = [("John", 30), ("Jane", 25)]
    db_instance.insert_data("test_table", data, ["name", "age"])
    rows = db_instance.fetch_all("test_table")
    assert len(rows) == 2
    assert rows[0]["name"] == "John"
    assert rows[1]["age"] == 25

def test_update_data(db_instance):
    """Test updating data."""
    db_instance.create_table("test_table", [
        ("id", "INTEGER PRIMARY KEY"),
        ("name", "TEXT"),
        ("age", "INTEGER")
    ])
    db_instance.insert_data("test_table", [("John", 30)], ["name", "age"])
    db_instance.update_data("test_table", "age", 35, "name", "John")
    rows = db_instance.search("test_table", "name", "John")
    assert rows[0]["age"] == 35

def test_search_data(db_instance):
    """Test searching data."""
    db_instance.create_table("test_table", [
        ("id", "INTEGER PRIMARY KEY"),
        ("name", "TEXT"),
        ("age", "INTEGER")
    ])
    data = [("Alice", 28), ("Bob", 40)]
    db_instance.insert_data("test_table", data, ["name", "age"])
    rows = db_instance.search("test_table", "name", "Alice")
    assert len(rows) == 1
    assert rows[0]["age"] == 28

def test_reset_database(db_instance, tmp_path):
    """Test resetting the database."""
    db_instance.create_table("test_table", [
        ("id", "INTEGER PRIMARY KEY"),
        ("name", "TEXT"),
        ("age", "INTEGER")
    ])
    db_instance.reset_database()
    tables = db_instance.return_custom_query(
        "SELECT name FROM sqlite_master WHERE type='table';"
    )
    assert len(tables) == 0

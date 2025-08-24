import pytest
from app.models import Entry


@pytest.fixture
def auth_client(client, test_user):
    """Authenticated client"""
    client.post("/api/auth/login", json={"password": "testpass123"})
    return client


@pytest.fixture
def searchable_entries(db_session, test_hobby, test_hobby_type):
    """Create entries for search testing"""
    entries = [
        Entry(
            hobby_id=test_hobby.id,
            type_key=test_hobby_type.key,
            title="Photography Tips",
            description="Learn about camera settings",
            tags="photography,camera"
        ),
        Entry(
            hobby_id=test_hobby.id,
            type_key=test_hobby_type.key,
            title="Cooking Recipe",
            description="Delicious pasta recipe",
            tags="cooking,food"
        ),
        Entry(
            hobby_id=test_hobby.id,
            type_key=test_hobby_type.key,
            title="Camera Review",
            description="Review of the new camera model",
            tags="photography,review"
        )
    ]
    
    for entry in entries:
        db_session.add(entry)
    db_session.commit()
    
    for entry in entries:
        db_session.refresh(entry)
    
    return entries


def test_search_basic_query(auth_client, searchable_entries):
    """Test basic text search"""
    response = auth_client.get("/api/search?q=photography")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    # Should find entries containing "photography"
    photography_entries = [item for item in data["items"] if "photography" in item["title"].lower() or "photography" in (item["tags"] or "")]
    assert len(photography_entries) > 0


def test_search_with_filters(auth_client, searchable_entries, test_hobby, test_hobby_type):
    """Test search with additional filters"""
    response = auth_client.get(f"/api/search?q=camera&hobby_id={test_hobby.id}")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    
    response = auth_client.get(f"/api/search?q=camera&type_key={test_hobby_type.key}")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_search_by_tag(auth_client, searchable_entries):
    """Test search by tag"""
    response = auth_client.get("/api/search?q=photography&tag=photography")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_search_pagination(auth_client, searchable_entries):
    """Test search pagination"""
    response = auth_client.get("/api/search?q=camera&limit=1&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data


def test_search_empty_query(auth_client):
    """Test search with empty query"""
    response = auth_client.get("/api/search?q=")
    assert response.status_code == 400
    data = response.json()
    assert "cannot be empty" in data["message"].lower()


def test_search_special_characters(auth_client):
    """Test search with special characters (should be sanitized)"""
    response = auth_client.get("/api/search?q=test;DROP TABLE;")
    assert response.status_code in [200, 400]  # Should be sanitized or rejected
    

def test_search_requires_auth(client):
    """Test that search requires authentication"""
    response = client.get("/api/search?q=test")
    assert response.status_code == 401
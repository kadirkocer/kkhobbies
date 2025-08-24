import pytest
import json


@pytest.fixture
def auth_client(client, test_user):
    """Authenticated client"""
    client.post("/api/auth/login", json={"password": "testpass123"})
    return client


def test_get_hobby_types(auth_client, test_hobby_type):
    """Test getting hobby types"""
    response = auth_client.get("/api/hobby-types")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["key"] == test_hobby_type.key


def test_create_hobby_type(auth_client):
    """Test creating a new hobby type"""
    schema = {
        "type": "object",
        "properties": {
            "brand": {"type": "string"},
            "model": {"type": "string"},
            "price": {"type": "number"}
        }
    }
    
    response = auth_client.post("/api/hobby-types", json={
        "key": "gear",
        "title": "Gear",
        "schema_json": json.dumps(schema)
    })
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "gear"
    assert data["title"] == "Gear"


def test_create_hobby_type_invalid_schema(auth_client):
    """Test creating hobby type with invalid JSON schema"""
    response = auth_client.post("/api/hobby-types", json={
        "key": "invalid",
        "title": "Invalid",
        "schema_json": "not valid json"
    })
    assert response.status_code == 400
    data = response.json()
    assert "Invalid JSON Schema" in data["message"]


def test_create_duplicate_hobby_type(auth_client, test_hobby_type):
    """Test creating hobby type with duplicate key"""
    schema = {"type": "object", "properties": {}}
    
    response = auth_client.post("/api/hobby-types", json={
        "key": test_hobby_type.key,
        "title": "Duplicate",
        "schema_json": json.dumps(schema)
    })
    assert response.status_code == 400
    data = response.json()
    assert "already exists" in data["message"]


def test_update_hobby_type(auth_client, test_hobby_type):
    """Test updating a hobby type"""
    response = auth_client.patch(f"/api/hobby-types/{test_hobby_type.key}", json={
        "title": "Updated Test Type"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Test Type"


def test_update_hobby_type_invalid_schema(auth_client, test_hobby_type):
    """Test updating hobby type with invalid schema"""
    response = auth_client.patch(f"/api/hobby-types/{test_hobby_type.key}", json={
        "schema_json": "invalid json"
    })
    assert response.status_code == 400
    data = response.json()
    assert "Invalid JSON Schema" in data["message"]


def test_delete_hobby_type(auth_client, test_hobby_type):
    """Test deleting a hobby type"""
    response = auth_client.delete(f"/api/hobby-types/{test_hobby_type.key}")
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = auth_client.get("/api/hobby-types")
    assert get_response.status_code == 200
    data = get_response.json()
    keys = [ht["key"] for ht in data]
    assert test_hobby_type.key not in keys


def test_hobby_types_require_auth(client, test_hobby_type):
    """Test that hobby types endpoints require authentication"""
    response = client.get("/api/hobby-types")
    assert response.status_code == 401
    
    response = client.post("/api/hobby-types", json={})
    assert response.status_code == 401
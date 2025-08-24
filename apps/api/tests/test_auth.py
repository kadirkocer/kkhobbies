import pytest
from app.auth import hash_password
from app.models import User


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post("/api/auth/login", json={
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["username"] == "testuser"


def test_login_invalid_password(client, test_user):
    """Test login with invalid password"""
    response = client.post("/api/auth/login", json={
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["status"] == 401
    assert "Invalid credentials" in data["message"]


def test_login_no_user(client):
    """Test login when no user exists"""
    response = client.post("/api/auth/login", json={
        "password": "testpass123"
    })
    assert response.status_code == 401


def test_logout(client):
    """Test logout endpoint"""
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Logged out successfully"


def test_me_endpoint_authenticated(client, test_user):
    """Test /me endpoint with authentication"""
    # First login
    login_response = client.post("/api/auth/login", json={
        "password": "testpass123"
    })
    assert login_response.status_code == 200
    
    # Then access /me
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


def test_me_endpoint_unauthenticated(client):
    """Test /me endpoint without authentication"""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
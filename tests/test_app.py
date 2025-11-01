import pytest
from fastapi.testclient import TestClient
from src.app import app

# Create test client
client = TestClient(app)

def test_root_redirect():
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test retrieving all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Check if we get a dictionary of activities
    assert isinstance(activities, dict)
    # Check if we have some activities
    assert len(activities) > 0
    
    # Check structure of an activity
    activity = list(activities.values())[0]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)

def test_signup_for_activity_success():
    """Test successful activity signup"""
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    
    # First ensure the email is not already registered
    response = client.get("/activities")
    activities = response.json()
    if email in activities[activity_name]["participants"]:
        # Remove the email if it's already there
        response = client.delete(f"/activities/{activity_name}/unregister/{email}")
        assert response.status_code == 200
    
    # Try to sign up
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]
    assert activity_name in result["message"]

def test_signup_for_activity_duplicate():
    """Test signing up for an activity twice"""
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"
    
    # First signup
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Try to signup again
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_for_nonexistent_activity():
    """Test signing up for an activity that doesn't exist"""
    response = client.post(
        "/activities/NonexistentClub/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_from_activity_success():
    """Test successful unregistration from an activity"""
    activity_name = "Chess Club"
    email = "unregister@mergington.edu"
    
    # First sign up for the activity
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Then unregister
    response = client.delete(f"/activities/{activity_name}/unregister/{email}")
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]
    assert activity_name in result["message"]

def test_unregister_from_activity_not_registered():
    """Test unregistering when not registered"""
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    
    response = client.delete(f"/activities/{activity_name}/unregister/{email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_from_nonexistent_activity():
    """Test unregistering from an activity that doesn't exist"""
    response = client.delete(
        "/activities/NonexistentClub/unregister/test@mergington.edu"
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
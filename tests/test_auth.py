def test_login_invalid_credentials(client):
    response = client.post(
        "/login",
        json={
            "username": "wrong_admin",
            "password": "wrong_password"
        }
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid username or password"
def test_login_success(client):
    response = client.post(
        "/login",
        json={
            "username": "college_admin",
            "password": "StudentMgmt@2026"
        }
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Login successful"   
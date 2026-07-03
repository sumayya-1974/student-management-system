def test_students_requires_login(client):
    response = client.get("/students")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Login required"
def test_view_students_after_login(client):
    login_response = client.post(
        "/login",
        json={
            "username": "college_admin",
            "password": "StudentMgmt@2026"
        }
    )

    assert login_response.status_code == 200

    response = client.get("/students")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
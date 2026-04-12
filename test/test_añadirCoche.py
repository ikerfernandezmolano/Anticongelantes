def test_añadirCoche(client):
    response = client.post("/add_car", data={
        "marca": "BMW",
        "modelo": "M3",
        "precio": 60000,
        "kilometraje": 10000,
        "imagen": "bmw.jpg"
    }, follow_redirects=True)

    assert response.status_code == 200
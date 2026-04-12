def test_delete_car(client):

    # Crear coche
    client.post("/add_car", data={
        "marca": "Audi",
        "modelo": "A4",
        "precio": 30000,
        "kilometraje": 50000,
        "imagen": "audi.jpg"
    }, follow_redirects=True)

    # Eliminar directamente (id = 1 porque es el primero)
    response = client.get("/delete_car/1", follow_redirects=True)
    assert response.status_code == 200

    # Verificar que ya no está
    response = client.get("/catalogo", follow_redirects=True)
    assert "Audi" not in response.data.decode()
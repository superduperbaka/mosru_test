def test_read_main(backend_api):
    response = backend_api.get('/')
    assert response.status_code == 200

import pytest
from app import create_app

from app.models.map_data import MapData

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_getMapData(client, mocker):
    # Mock the MapData.query.all() method
    mock_data = [MapData(id=1, name='Test Data')]
    mocker.patch('app.models.map_data.MapData.query.all', return_value=mock_data)

    response = client.post('/map/')
    assert response.status_code == 200
    assert response.json == mock_data
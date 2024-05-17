from typing import Callable
from typing import List
from typing import Optional
from typing import Union
from uuid import UUID

import pytest
from deprecated import deprecated
from factory import Factory
from pydantic import BaseModel

from tests.conftest import validate_datetime
from tests.factories import convert_dict_from_stub


@deprecated(
    "This class is depracted, we created for tests puporse but pytest does not works well with inhiritance with __init__"
)
class BaseTest:
    def __init__(
        self,
        base_url: str,
        setup_func: Callable,
        base_schema: BaseModel,
        model_factory: Factory,
        model_name: str,
        base_input_keys: List[str],
        id_type: Optional[Union[int, UUID]] = UUID,
    ) -> None:
        self.base_url = base_url
        self.setup_func = setup_func
        self.base_schema = base_schema
        self.model_factory = model_factory
        self.model_name = model_name
        self.id_type = id_type
        self.base_input_keys = base_input_keys

    def validate_id(self, id: Union[int, UUID]) -> bool:
        if isinstance(id, UUID):
            return True
        return isinstance(id, int)

    # @pytest.mark.anyio
    # async def get_all_users_should_return_200_ok_GET(self, session, client):
    #     clean_models = await self.setup_func(session, 8)
    #     clean_models = [model.model_json_dump() for model in clean_models]

    #     response = await client.get(f"{self.base_url}/?offset=0&limit=100")
    #     response_json = response.json()

    #     assert response.status_code == 200
    #     assert response_json["search_options"] == {"limit": 100, "offset": 0, "total_count": 8}

    #     model_founds_json = response_json["founds"]
    #     assert len(model_founds_json) == 8
    #     assert all([validate_datetime(model["created_at"]) for model in model_founds_json])
    #     assert all([validate_datetime(model["updated_at"]) for model in model_founds_json])
    #     assert all([all([model[key] == value for model in model_founds_json]) for key, value in clean_models.items()])

    # @pytest.mark.anyio
    # async def test_get_all_users_with_limit_should_return_200_OK(self, session, client):
    #     limit = 5
    #     clean_models = await self.setup_func(session, 8)
    #     clean_models = [model.model_json_dump() for model in clean_models]
    #     response = await client.get(f"{self.base_url}/?offset=0&limit={limit}")
    #     response_json = response.json()
    #     model_founds_json = response_json["founds"]

    #     assert response.status_code == 200
    #     assert len(model_founds_json) == 5
    #     assert response_json["search_options"] == {"limit": limit, "offset": 0, "total_count": limit}
    #     assert all([validate_datetime(model["created_at"]) for model in model_founds_json])
    #     assert all([validate_datetime(model["updated_at"]) for model in model_founds_json])
    #     assert all([all(model[key] == value for model in model_founds_json) for key, value in clean_models.items()])
    #     for count, clean_model in enumerate(clean_models[:limit]):
    #         assert all([model_founds_json[count][key] == value for key, value in clean_model.items()])

    # @pytest.mark.anyio
    # async def test_get_all_users_with_offset_should_return_200_OK(self, session, client):
    #     offset = 3
    #     clean_models = await self.setup_func(session, 8)
    #     clean_models = [model.model_json_dump() for model in clean_models]
    #     response = await client.get(f"{self.base_url}/?offset={offset}&limit=100")
    #     response_json = response.json()
    #     model_founds_json = response_json["founds"]

    #     assert response.status_code == 200
    #     for count, clean_model in enumerate(clean_models[offset:]):
    #         assert all([model_founds_json[count][key] == value for key, value in clean_model.items()])
    #     assert len(model_founds_json) == 5
    #     assert response_json["search_options"] == {"limit": 100, "offset": offset, "total_count": 5}
    #     assert all([validate_datetime(model["created_at"]) for model in model_founds_json])
    #     assert all([validate_datetime(model["updated_at"]) for model in model_founds_json])

    # @pytest.mark.anyio
    # async def test_get_all_users_with_pagination_should_return_200_OK(self, session, client):
    #     offset = 2
    #     limit = 3
    #     clean_models = await self.setup_func(session, 8)
    #     clean_models = [model.model_json_dump() for model in clean_models]
    #     response = await client.get(f"{self.base_url}/?offset={offset}&limit={limit}")
    #     response_json = response.json()
    #     model_founds_json = response_json["founds"]

    #     assert response.status_code == 200
    #     for count, clean_model in enumerate(clean_models[offset : limit + offset]):
    #         assert all([model_founds_json[count][key] == value for key, value in clean_model.items()])
    #     assert len(model_founds_json) == limit
    #     assert response_json["search_options"] == {"limit": limit, "offset": offset, "total_count": limit}
    #     assert all([validate_datetime(model["created_at"]) for model in model_founds_json])
    #     assert all([validate_datetime(model["updated_at"]) for model in model_founds_json])

    def get_input_model(self, factory_instance):
        factory_dict = convert_dict_from_stub(factory_instance)
        input_schema_dict = {key: factory_dict[key] for key in self.base_input_keys}
        return self.base_schema(**input_schema_dict)

    @pytest.mark.anyio
    async def test_create_should_return_201_POST(self, client, session):
        factory_model = self.model_factory()
        input_schema = self.get_input_model(factory_model)

        response = await client.post(f"{self.base_url}/", json={**input_schema})
        response_json = response.json()

        assert response.status_code == 201
        assert self.validate_id(response_json["id"])
        assert all([response_json[key] == value for key, value in input_schema])
        assert validate_datetime(response_json["created_at"])
        assert validate_datetime(response_json["updated_at"])

    @pytest.mark.anyio
    async def test_create_should_return_422_unprocessable_entity_POST(self, client):
        response = await client.post(
            f"{self.base_url}/",
        )

        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_create_should_return_409_email_already_registered_POST(self, client, session):
        clean_models = await self.setup_func(session, 1)
        clean_model = clean_models[0]
        clean_model_json = clean_model.model_dump_json()
        response = await client.post(
            f"{self.base_url}/",
            json={**clean_model_json},
        )

        assert response.status_code == 409
        assert response.json() == {"detail": f"{self.model_name} already registered"}

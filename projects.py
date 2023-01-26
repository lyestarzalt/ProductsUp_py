from dataclasses import dataclass
from typing import List


@dataclass
class Project:
    project_id: str
    name: str
    created_at: str
    links: List


class Projects:
    BASE_URL = "https://platform-api.productsup.io/platform/v2/projects"

    def __init__(self, auth) -> None:
        self.auth = auth

    def list_all_projects(self) -> list[Project]:
        url = f"{self.BASE_URL}/"
        response = self.auth.make_request(url, method='get')
        data = response.json()
        if not data["success"]:
            raise Exception(data["error"])
        return [Project(**project_data) for project_data in data["Projects"]]

    def get_project(self, project_id: int) -> Project:
        url = f"{self.BASE_URL}/{project_id}"
        response = self.auth.make_request(url, method='get')
        data = response.json()
        if not data["success"]:
            raise Exception(data["error"])
        return Project(**data["Projects"][0])

    def create_project(self, name: str) -> Project:
        data = {'name': name}
        url = f"{self.BASE_URL}/"
        response = self.auth.make_request(url, method='post', json=data)
        data = response.json()
        if not data["success"]:
            raise Exception(data["error"])
        return Project(**data["Projects"][0])

    def update_project(self, project_id, data):
        url = f"{self.BASE_URL}/{project_id}"
        response = self.auth.make_request(url, method='put', data=data)
        return response.json()

    def delete_project(self, project_id):
        url = f"{self.BASE_URL}/{project_id}"
        response = self.auth.make_request(url, method='delete')
        return response.json()

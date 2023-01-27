# Author: Lyes Tarzalt
from dataclasses import dataclass, field
from typing import List
from productsup_py.productup_exception import ProductsUpError


@dataclass
class Project:
    project_id: str
    name: str
    created_at: str
    links: List = field(repr=False)


class Projects:

    BASE_URL = "https://platform-api.productsup.io/platform/v2/projects"

    def __init__(self, auth) -> None:
        self.auth = auth

    def list_all_projects(self) -> list[Project]:
        url = f"{Projects.BASE_URL}"
        response = self.auth.make_request(url, method='get')
        data = response
        if not data["success"]:
            raise ProductsUpError(data["error"])
        projects_data = [{'project_id': project_data.pop(
            'id'), **project_data} for project_data in data["Projects"]]

        return [Project(**project_data) for project_data in projects_data]
    

    def get_project(self, project_id: int) -> Project:
        _url = f"{Projects.BASE_URL}/{project_id}"
        response = self.auth.make_request(_url, method='get')
        if not response["success"]:
            raise ProductsUpError(response["error"])
        projects_data = [{'project_id': project_data.pop(
            'id'), **project_data} for project_data in response["Projects"]]
        return Project(**projects_data[0])
    

    def create_project(self, project_name: str) -> Project:
        data = {'name': project_name}
        url = f"{Projects.BASE_URL}/"
        response = self.auth.make_request(url, method='post', json=data)
        
        if not response["success"]:
            raise ProductsUpError(response.status_code, response["message"])
        projects_data = [{'project_id': project_data.pop(
            'id'), **project_data} for project_data in response["Projects"]]
        return Project(**projects_data[0])


    def update_project(self, project_id, data: Project):
        url = f"{Projects.BASE_URL}/{project_id}"
        response = self.auth.make_request(url, method='put', data=data)
        if not response.get("success", False):
            raise ProductsUpError(response.status_code, data["message"])
        projects_data = [{'project_id': project_data.pop(
            'id'), **project_data} for project_data in response["Projects"]]
        return Project(**projects_data[0])

    def delete_project(self, project_id):
        url = f"{Projects.BASE_URL}/{project_id}"
        response = self.auth.make_request(url, method='delete')
        if not response.get("success", False):
            raise ProductsUpError(response.status_code,
                                  response.get("message"))   
        return 'Project deleted successfully'

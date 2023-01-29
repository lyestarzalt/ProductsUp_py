# Author: Lyes Tarzalt
from dataclasses import dataclass, field
import json
from typing import List
from productsup_py.errors.productup_exception import ProductsUpError

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
        """Lists all or one projects in your account .

        Raises:
            ProductsUpError

        Returns:
            list[Project]: List of Project objects
        """        
        
        url = f"{Projects.BASE_URL}"
        response = self.auth.make_request(url, method='get')
        response_body = response.json()
        if not response_body.get("success", False):
            raise ProductsUpError(response_body.get("message"))
        projects_data = [{'project_id': project_data.pop(
            'id'), **project_data} for project_data in response_body.get("Projects", [])]

        return [Project(**project_data) for project_data in projects_data]

    def get_project(self, project_id: int) -> Project:
        """Get a specific project by its ID.

        Args:
            project_id (int): project id

        Raises:
            ProductsUpError

        Returns:
            Project: Project object
        """        
        _url = f"{Projects.BASE_URL}/{project_id}"
        response = self.auth.make_request(_url, method='get')
        response_body = response.json()

        if not response_body.get('success', False):
            raise ProductsUpError(response_body.get("message"))
    
        projects_data = [{'project_id': project_data.pop(
            'id'), **project_data} for project_data in response_body.get("Projects")]
        return Project(**projects_data[0])

    def create_project(self, project_name: str) -> Project:
        """Create a new project.

        Args:
            project_name (str): Project name

        Raises:
            ProductsUpError

        Returns:
            Project: Project object
        """        
        
        url = f"{Projects.BASE_URL}"
        response = self.auth.make_request(
            url, method='post', data=json.dumps({'name': project_name}))
        
        response_body = response.json()
        
        if not response_body.get("success", False):
            raise ProductsUpError(response.status_code,
                                  response_body["message"])
        projects_data = [{'project_id': project_data.pop(
            'id'), **project_data} for project_data in response_body.get("Projects")]
        return Project(**projects_data[0])

    def update_project(self, project_id, name: str):
        """Update a project.

        Args:
            project_id (_type_): project id
            name (str): project name

        Raises:
            ProductsUpError: 

        Returns:
            _type_: Project object
        """        
        url = f"{Projects.BASE_URL}/{project_id}"
        response = self.auth.make_request(url, method='put', data=json.dumps({"name": name}))
        response_body = response.json()
        if not response.get("success", False):
            raise ProductsUpError(response.status_code,
                                  response_body.get("message"))
        projects_data = [{'project_id': project_data.pop(
            'id'), **project_data} for project_data in response_body.get("Projects")]
        return Project(**projects_data[0])

    def delete_project(self, project_id) -> bool:
        """Delete a project.

        Args:
            project_id (_type_): project id

        Raises:
            ProductsUpError: 

        Returns:
            str: _description_
        """        
        url = f"{Projects.BASE_URL}/{project_id}"
        response = self.auth.make_request(url, method='delete')
        response_body = response.json()
        if not response_body.get("success", False):
            raise ProductsUpError(response.status_code,
                                  response_body.get("message"))
            
        return True

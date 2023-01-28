# Author: Lyes Tarzalt
from productsup_py.productup_exception import ProductsUpError, SiteNotFoundError, EmptySiteError
from productsup_py.projects import Projects
from productsup_py.models import SiteStatus, SiteProcessingStatus, \
    SiteImport, SiteChannelHistory, SiteChannel, SiteError, Site, Project
from datetime import datetime
import json


class Sites:
    BASE_URL = 'https://platform-api.productsup.io/platform/v2'

    def __init__(self, auth) -> None:
        self.auth = auth
        self.projects = Projects(auth)

    @staticmethod
    def str_to_datetime(date: str) -> datetime:
        try:
            return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.strptime(date, '%Y-%m-%d')
        except TypeError:
            return datetime(1970, 1, 1)

    def _get_channels(self, site_id: int) -> list[SiteChannel]:
        _url = f"{Sites.BASE_URL}/sites/{site_id}/channels"
        response = self.auth.make_request(_url, method='get')
        response_body = response.json()
        if not response_body.get("success", False):
            raise ProductsUpError(response["error"])

        channel_data = []
        for channel in response_body['Channels']:
            channel['entity_id'] = channel.pop('id')
            channel['export_history'] = self._get_channel_history(
                site_id, channel['entity_id'])
            channel_data.append(channel)
        return [SiteChannel(**channel) for channel in channel_data]

    def _get_channel_history(self, site_id: int, channel_id: int) -> list[SiteChannelHistory]:
        _url = f"{Sites.BASE_URL}/sites/{site_id}/channels/{channel_id}/history"
        response = self.auth.make_request(_url, method='get')
        response_body = response.json()
        if not response_body.get("success", False):
            raise ProductsUpError(response_body["message"])

        channel_history_data = []
        for channel_history in response_body.get('Channels')[0].get('history'):
            channel_history['history_id'] = channel_history.pop('id')
            channel_history_data.append(channel_history)
        return [SiteChannelHistory(**channel_history) for channel_history in channel_history_data]

    def _get_errors(self, site_id: int) -> list[SiteError]:
        _url = f"{Sites.BASE_URL}/sites/{site_id}/errors"
        response = self.auth.make_request(_url, method='get')
        response_body = response.json()
        if not response_body.get("success", False):
            raise ProductsUpError(response["error"])

        error_data = []
        for error in response_body.get('Errors'):
            error['error_id'] = error.pop('id')
            if error.get('datetime',None): 
                # rename datetime to error_datetime because datetime is we have a class with the same name
                error['error_datetime'] = error.pop('datetime')
                error['error_datetime'] = self.str_to_datetime(
                    error['error_datetime'])

            error_data.append(error)
        return [SiteError(**error) for error in error_data]

    def _get_imports(self, site_id: int) -> list[SiteImport]:
        url = f"{Sites.BASE_URL}/sites/{site_id}/importhistory"
        response = self.auth.make_request(url, method='get')
        response_body = response.json()
        if not response_body.get("success", False):
            raise ProductsUpError(response["error"])
        import_data = []
        if not response_body.get('Importhistory'):
            return []
        for import_ in response_body['Importhistory']:
            import_['import_id'] = import_.pop('id')
            import_['import_time'] = self.str_to_datetime(
                import_['import_time'])
            import_['import_time_utc'] = self.str_to_datetime(
                import_['import_time_utc'])
            import_data.append(import_)
        return [SiteImport(**import_) for import_ in import_data]

    def _construct_site(self, response: str, site_id: int) -> Site:
        site_data = response.json().get("Sites", [])  # type: ignore
        if not site_data:
            raise EmptySiteError()
        site_data = site_data[0]
        site_data['site_id'] = site_data.pop('id')
        site_data['project'] = site_data.pop('project_id')
        site_data['project'] = self.projects.get_project(site_data['project'])
        site_data['created_at'] = self.str_to_datetime(
            date=site_data['created_at'])
        site_data['processing_status'] = SiteProcessingStatus(
            site_data['processing_status']).value
        site_data['status'] = SiteStatus(site_data['status']).value
        site_data.pop('links')
        site_data.pop('availableProjectIds')
        site_data['import_history'] = self._get_imports(site_id)
        site_data['channels'] = self._get_channels(site_id)
        site_data['errors'] = self._get_errors(site_id)
        return Site(**site_data)

    def get_site(self, site_id: int) -> Site:

        url = f"{Sites.BASE_URL}/sites/{site_id}"
        try:
            response = self.auth.make_request(url, method='get')
        except ProductsUpError as e:
            if e.status_code == 404:
                raise SiteNotFoundError(site_id=site_id)
            else:
                raise e
        return self._construct_site(response=response, site_id=site_id)

    def get_all_sites(self) -> list[Site]:

        url = f"{Sites.BASE_URL}/sites"
        response = self.auth.make_request(url, method='get')

        if not response.get("success", False):
            raise ProductsUpError(response["error"])

        sites_data = []
        for site_data in response["Sites"]:
            site_data['site_id'] = site_data.pop('id')
            site_data['project'] = site_data.pop('project_id')
            site_data['available_project_ids'] = site_data.pop(
                'availableProjectIds')
            site_data.pop('links', None)
            site_data.pop('availableProjectIds ', None)
            sites_data.append(site_data)

        return [Site(**site_data) for site_data in sites_data]

    def create_site(self, project_id: int, title: str, import_schedule: str = None, reference: str = None,  # type: ignore
                    id_column: str = None, status: str = None):  # type: ignore
        data = {
            "title": title,
            "reference": reference,
            "import_schedule": import_schedule
        }
        if id_column:
            data["id_column"] = id_column
        if status:
            data["status"] = status
        _url = f"{Sites.BASE_URL}/{project_id}/sites"
        response = self.auth.make_request(_url, method='post', data=data)
        return response

    def edit_site(self, site_id, title=None, reference=None,
                  project_id=None, id_column=None, status=None, import_schedule=None):
        site_info: Site = self.get_site(site_id)

        # To simplify the process of editing the import schedule, we will accept a
        # dict with the keys "TZ" and "cron" and convert it to the correct format
        # NOTE: there is a bug with the api when setting UTC as the timezone.
        if import_schedule is not None and isinstance(import_schedule, dict):
            import_schedule = f"{import_schedule.get('TZ', 'UTC')}\n{import_schedule.get('cron')}"
        else:
            import_schedule = site_info.import_schedule

        data = {
            'id': site_id,
            'title': title if title is not None else site_info.title,
            'project_id': project_id if project_id is not None else site_info.project.project_id,  # type: ignore
            'id_column': id_column if id_column is not None else site_info.id_column,
            'status': status if status is not None else site_info.status,
            'import_schedule': import_schedule
        }
        url = f'{Sites.BASE_URL}/sites/{site_id}'
        response = self.auth.make_request(
            url, method='put', data=json.dumps(data))
        response_body = response.json()
        if not response_body.get("success", False):
            raise ProductsUpError(
                status_code=response.status_code, message=response_body.get("message"))

        return self._construct_site(response=response, site_id=site_id)

    def delete_site(self, site_id: int):
        url = f"{Site.BASE_URL}/sites/{site_id}"  # type: ignore
        response = self.auth.make_request(url, method='delete')
        if not response.get("success", False):
            raise ProductsUpError(response.status_code,
                                  response.get("message"))
        return 'Site deleted successfully'

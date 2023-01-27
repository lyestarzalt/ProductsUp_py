# Author: Lyes Tarzalt
from enum import Enum
from dataclasses import dataclass
from productsup_py.productup_exception import ProductsUpError, SiteNotFoundError, InvalidDataError, EmptySiteError
from productsup_py.projects import Projects, Project
from datetime import datetime
import json
from typing import List, Union


class SiteStatus(Enum):
    # The site is fully operational; data can be pushed via the API and
    # the site will import and export
    ACTIVE = "active"
    # The site can receive data via the API and import the data; it will
    # however not export data
    PAUSED_UPLOAD = "paused_upload"
    # The site will block any data send via the API, neither imports or
    # exports can be done
    DISABLED = "disabled"


class SiteProcessingStatus(Enum):

    RUNNING = "Running"
    DONE = "Done"


@dataclass
class SiteImport:
    """ A site import is a record of the import of a site."""

    import_id: int
    site_id: int
    import_time: datetime
    import_time_utc: datetime
    product_count: int
    pid: str
    links: list = None


@dataclass
class SiteChannelHistory:
    """ A site channel history is a record of the export of a site to a channel."""

    history_id: int
    site_id: int
    site_channel_id: int
    export_time: str
    export_start: str
    product_count: int
    pid: str
    product_count_new: int
    product_count_modified: int
    product_count_deleted: int
    product_count_unchanged: int
    uploaded: int
    product_count_now: int
    product_count_previous: int
    product_count_skipped: int
    process_status: SiteProcessingStatus


@dataclass
class SiteChannel:
    """ Channels are targets of the data (like "Google Shopping", Export csv,..)"""

    entity_id: int
    site_id: int
    channel_id: int
    name: str
    export_name: str
    feed_destinations: list
    export_history: SiteChannelHistory
    links: list = None


@dataclass
class SiteError:
    """A site error is an error that occurred during the import or export of a site."""

    error_id: int
    pid: str
    error: int
    data: list
    site_id: int
    message: str
    datetime: str = None
    links: list = None


@dataclass
class Site:
    """Sites are the smallest entity, below projects, in the Productsup platform."""

    site_id: int
    title: str
    status: SiteStatus
    # incase of get_site it will be a project object and in case of get_all_sites it will be an int
    project: Union[Project, int]
    import_schedule: str
    id_column: str
    processing_status: SiteProcessingStatus
    created_at: datetime = None
    import_history: list[SiteImport] = None
    errors: list[SiteError] = None
    channels: list[SiteChannel] = None
    links: list = None


class Sites:

    BASE_URL = 'https://platform-api.productsup.io/platform/v2'

    def __init__(self, auth) -> None:
        self.auth = auth
        self.projects = Projects(auth)

    def str_to_datetime(self, date: str) -> datetime:
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

    def _constract_site(self, response: str, site_id: int) -> Site:
        site_data = response.json().get("Sites", [])
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
        return self._constract_site(response=response, site_id=site_id)

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

    def create_site(self, project_id: int, title: str, import_schedule: str, reference: str = None, id_column: str = None, status: str = None):
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
        site_info = self.get_site(site_id)
        
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
            'project_id': project_id if project_id is not None else site_info.project.project_id,
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

        return self._constract_site(response=response, site_id=site_id)

    def delete_site(self, site_id: int):
        url = f"{Site.BASE_URL}/sites/{site_id}"
        response = self.auth.make_request(url, method='delete')
        if not response.get("success", False):
            raise ProductsUpError(response.status_code,
                                  response.get("message"))
        return 'Site deleted successfully'

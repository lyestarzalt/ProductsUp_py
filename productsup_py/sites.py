# Author: Lyes Tarzalt
from enum import Enum
from dataclasses import dataclass
from productsup_py.productup_exception import ProductsUpError, SiteNotFoundError, EmptySiteError
from productsup_py.projects import Project, Projects
from datetime import datetime


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
    import_id: int
    site_id: int
    import_time: str
    import_time_utc: str
    product_count: int
    pid: str
    links: list = None


@dataclass
class SiteChannelHistory:
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
    """
    Sites are the smallest entity, below projects, in the Productsup platform.
    """
    site_id: int
    title: str
    status: SiteStatus
    project: any
    import_schedule: str
    id_column: str
    processing_status: SiteProcessingStatus
    created_at: str = None
    import_history: list[SiteImport] = None
    errors: list[SiteError] = None
    channels: list[SiteChannel] = None
    links: list = None


class Sites:
    BASE_URL = 'https://platform-api.productsup.io/platform/v2'

    def __init__(self, auth) -> None:
        self.auth = auth
        self.projects = Projects(auth)

    def _get_channels(self, site_id: int) -> list[SiteChannel]:
        _url = f"{Sites.BASE_URL}/sites/{site_id}/channels"
        response = self.auth.make_request(_url, method='get')

        if not response.get("success", False):
            raise ProductsUpError(response["error"])

        channel_data = []
        for channel in response['Channels']:
            channel['entity_id'] = channel.pop('id')
            channel['export_history'] = self._get_channel_history(
                site_id, channel['entity_id'])
            channel_data.append(channel)

        return [SiteChannel(**channel) for channel in channel_data]

    def _get_channel_history(self, site_id: int, channel_id: int) -> list[SiteChannelHistory]:
        _url = f"{Sites.BASE_URL}/sites/{site_id}/channels/{channel_id}/history"
        response = self.auth.make_request(_url, method='get')

        if not response.get("success", False):
            raise ProductsUpError(response["error"])

        channel_history_data = []
        for channel_history in response.get('Channels')[0].get('history'):
            channel_history['history_id'] = channel_history.pop('id')
            channel_history_data.append(channel_history)
        return [SiteChannelHistory(**channel_history) for channel_history in channel_history_data]

    def _get_errors(self, site_id: int) -> list[SiteError]:
        """_summary_

        Args:
            site_id (int): _description_

        Raises:
            ProductsUpError: _description_

        Returns:
            list[SiteError]: _description_
        """
        _url = f"{Sites.BASE_URL}/sites/{site_id}/errors"
        response = self.auth.make_request(_url, method='get')

        if not response.get("success", False):
            raise ProductsUpError(response["error"])

        error_data = []
        for error in response['Errors']:
            error['error_id'] = error.pop('id')

            error_data.append(error)
        return [SiteError(**error) for error in error_data]

    def _get_imports(self, site_id: int) -> list[SiteImport]:
        url = f"{Sites.BASE_URL}/sites/{site_id}/importhistory"
        response = self.auth.make_request(url, method='get')

        if not response.get("success", False):
            raise ProductsUpError(response["error"])
        import_data = []
        for import_ in response['Importhistory']:
            import_['import_id'] = import_.pop('id')
            import_data.append(import_)
        return [SiteImport(**import_) for import_ in import_data]

    def get_site(self, site_id: int) -> Site:
        """ Get all the information related to a site

        Args:
            site_id (int): Site ID the unique identifier of a site

        Raises:
            SiteNotFoundError: if the site_id is not found
            SiteNotFoundError: _description_

        Returns:
            Site: Site object
        """
        url = f"{Sites.BASE_URL}/sites/{site_id}"
        try:
            response = self.auth.make_request(url, method='get')
        except ProductsUpError as e:
            if e.status_code == 404:
                raise SiteNotFoundError(site_id=site_id)
            else:
                raise e

        site_data = response.json().get("Sites", [])
        if not site_data:
            raise EmptySiteError()
        site_data = site_data[0]
        site_data['site_id'] = site_data.pop('id')
        site_data['project'] = site_data.pop('project_id')
        site_data['project'] = self.projects.get_project(site_data['project'])

        site_data['processing_status'] = SiteProcessingStatus(
            site_data['processing_status']).value
        site_data['status'] = SiteStatus(site_data['status']).value
        site_data.pop('links')
        site_data.pop('availableProjectIds')
        site_data['import_history'] = self._get_imports(site_id)
        site_data['channels'] = self._get_channels(site_id)
        site_data['errors'] = self._get_errors(site_id)
        return Site(**site_data)

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

    def create_site(self, project_id: int, title: str, reference: str, import_schedule: str, id_column: str = None, status: str = None):
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
        data = {
            'title': title if title is not None else site_info['title'],
            'reference': reference if reference is not None else site_info['reference'],
            'project_id': project_id if project_id is not None else site_info['project_id'],
            'id_column': id_column if id_column is not None else site_info['id_column'],
            'status': status if status is not None else site_info['status'],
            'import_schedule': import_schedule if import_schedule is not None else site_info['import_schedule'],
        }
        url = f'{Sites.BASE_URL}/sites/{site_id}'
        self.auth.make_request(url, method='put', json=data)

    def delete_site(self, site_id: int):
        url = f"{Site.BASE_URL}/sites/{site_id}"
        response = self.auth.make_request(url, method='delete')
        if not response.get("success", False):
            raise ProductsUpError(response.status_code,
                                  response.get("message"))
        return 'Site deleted successfully'

# Author: Lyes Tarzalt
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Union

""" Each dataclass is a model of the data returned by the API
"""
@dataclass
class Project:

    project_id: str
    name: str
    created_at: str
    links: Union[list, None] = field(default_factory=list, repr=False)


class SiteStatus(Enum):
    # The site is fully operational; data can be pushed via the API and
    # the site will import and export
    ACTIVE = "active"
    # The site can receive data via the API and import the data; it will
    # however not export data
    PAUSED_UPLOAD = "paused_upload"
    # The site will block any data send via the API, neither imports nor
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
    links: Union[list, None] = field(default_factory=list, repr=False)


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
    links: Union[list, None] = field(default_factory=list, repr=False)


@dataclass
class SiteError:
    """A site error is an error that occurred during the import or export of a site."""

    error_id: int
    pid: str
    error: int
    data: list
    site_id: int
    message: str
    error_datetime: Union[datetime,None] = None
    links: Union[list, None] = field(default_factory=list, repr=False)


@dataclass
class Site:
    """Sites are the smallest entity, below projects, in the Productsup platform."""

    site_id: int
    title: str
    status: SiteStatus
    # in case of get_site it will be a project object and in case of get_all_sites it will be an int
    project: Union[Project, int]
    import_schedule: str
    id_column: str
    processing_status: SiteProcessingStatus
    created_at: datetime
    import_history: list[SiteImport] = field(default_factory=list)
    errors: list[SiteError] = field(default_factory=list)
    channels: list[SiteChannel] = field(default_factory=list)
    links: Union[list, None] = field(default_factory=list, repr=False)

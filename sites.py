# Author: Lyes Tarzalt
from enum import Enum
from dataclasses import dataclass


class SiteStatus(Enum):
    # The site is fully operational; data can be pushed via the API and
    # the site will import and export
    ACTIVE = "active"
    # he site can receive data via the API and import the data;
    # it will however not export data
    PAUSED_UPLOAD = "paused_upload"
    # The site will block any data send via the API, neither imports or exports can be done
    DISABLED = "disabled"


class ProcessingStatus(Enum):
    # Site is queued (default when PID is valid, but not yet visible)
    QUEUED = "queued"
    # Site is being processed
    RUNNING = "running"
    # Site has run, no errors found
    SUCCESS = "success"
    # Site has run, but errors were found
    FAILED = "failed"


@dataclass
class Site:
    """
    Sites are the smallest entity, below projects, in the Productsup platform.
    """
    site_id: int
    title: str
    status: SiteStatus
    project_id: int
    import_schedule: str
    id_column: str
    processing_status: ProcessingStatus
    created_at: str
    links: list


class Sites:
    BASE_URL = 'https://platform-api.productsup.io/platform/v2/sites'

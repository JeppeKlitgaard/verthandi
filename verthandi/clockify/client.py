"""
Contains the Clockify REST Client
"""
from typing import Any, Dict, List, Literal, Optional, Union
from urllib.parse import urlparse, urlunparse

import orjson as json

import requests

from verthandi.config import settings

from .typing import Defaults


class ClockifyClient:
    """
    A Clockify REST API client.

    Attributes:
        api_key (str): The Clockify API Token to use
    """

    def __init__(self, api_key: Union[str, None], base_url: Optional[str] = None):
        if base_url is None:
            base_url = settings.BASE_URL

        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-Api-Key": api_key or "",
                "Content-Type": "application/json",
            }
        )

        self._base_url: str = base_url

        # Setup default workspace and user
        user_data = self.get_user()
        self._defaults: Defaults = {
            "workspaceId": user_data["defaultWorkspace"],
            "userId": user_data["id"],
        }

    @property
    def _reports_base_url(self) -> str:
        """
        Returns the reports base url

        Returns:
            str: reports base url
        """

        url_tuple = urlparse(self._base_url)
        url_tuple = url_tuple._replace(
            netloc=url_tuple.netloc.replace("api", "reports", 1)
        )

        return urlunparse(url_tuple)

    def _get_url(
        self,
        endpoint: str,
        url_type: Optional[Literal["report", "workspace", "workspace_user"]] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Returns the appropriate url for a given endpoint

        Args:
            endpoint (str): Endpoint without leading slash.
            url_type (Optional[Literal['report', 'workspace', 'workspace_user')]]:
                Whether to do special handling of url.
                Defaults to None
            workspace_id (Optional[str]): workspace_id to use.
                If None the default workspace will be used.
                Defaults to None.
            user_id (Optional[str]): user_id to use.
                If None the default user will be used.
                Defaults to None.

        Returns:
            str: url
        """

        if url_type == "report":
            return self._reports_base_url + "/" + endpoint

        if url_type == "workspace":
            if workspace_id is None:
                workspace_id = self._defaults["workspaceId"]

            return f"{self._base_url}/workspaces/{workspace_id}/{endpoint}"

        if url_type == "workspace_user":
            if workspace_id is None:
                workspace_id = self._defaults["workspaceId"]

            if user_id is None:
                user_id = self._defaults["userId"]

            return (
                f"{self._base_url}/workspaces/{workspace_id}/user/{user_id}/{endpoint}"
            )

        return self._base_url + "/" + endpoint

    def get_user(self) -> Dict[str, Any]:
        """
        Fetches the current user information

        Returns:
            dict: Dict of user information
        """
        url = self._get_url("user")

        req = self._session.get(url)

        return json.loads(req.text)

    def list_timeentry(
        self,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        url = self._get_url(
            "time-entries",
            url_type="workspace_user",
            workspace_id=workspace_id,
            user_id=user_id,
        )
        req = self._session.get(url, params=params)

        return json.loads(req.text)

    def start_timeentry(
        self,
        workspace_id: Optional[str] = None,
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = self._get_url(
            "time-entries", url_type="workspace", workspace_id=workspace_id
        )

        req = self._session.post(
            url, params=params, data=json.dumps(body, option=json.OPT_UTC_Z)
        )

        return json.loads(req.text)

    def stop_timeentry(
        self,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = self._get_url(
            "time-entries",
            url_type="workspace_user",
            workspace_id=workspace_id,
            user_id=user_id,
        )

        req = self._session.patch(
            url, params=params, data=json.dumps(body, option=json.OPT_UTC_Z)
        )

        return json.loads(req.text)

# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import json
import os
import time
from io import FileIO
from logging import WARNING
from mimetypes import guess_type
from typing import Any, Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, logger
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from .. import udB
from .helper import humanbytes, time_formatter

logger.setLevel(WARNING)


class GDriveManager:
    def __init__(self):
        self.gdrive_creds = {
            "oauth_scope": [
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/drive.metadata",
            ],
            "dir_mimetype": "application/vnd.google-apps.folder",
        }
        client_id = (
            udB.get_key("GDRIVE_CLIENT_ID")
            or "458306970678-jhfbv6o5sf1ar63o1ohp4c0grblp8qba.apps.googleusercontent.com"
        )
        client_secret = (
            udB.get_key("GDRIVE_CLIENT_SECRET")
            or "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"
        )
        self.client_secrets = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8080/"],
            }
        }
        self.token_file = "resources/auth/gdrive_creds.json"
        self.auth_token = udB.get_key("GDRIVE_AUTH_TOKEN")
        self.folder_id = udB.get_key("GDRIVE_FOLDER_ID")
        self.creds: Optional[Credentials] = None

        if self.auth_token:
            try:
                self.creds = Credentials.from_authorized_user_info(
                    json.loads(self.auth_token), self.gdrive_creds["oauth_scope"]
                )
            except (json.JSONDecodeError, ValueError):
                if os.path.exists(self.token_file):
                    os.remove(self.token_file)
                self.auth_token = None
                udB.del_key("GDRIVE_AUTH_TOKEN")

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                    if self.creds:
                        udB.set_key("GDRIVE_AUTH_TOKEN", self.creds.to_json())
                        with open(self.token_file, "w") as token:
                            token.write(self.creds.to_json())
                except Exception:
                    self.creds = None
                    if os.path.exists(self.token_file):
                        os.remove(self.token_file)
                    udB.del_key("GDRIVE_AUTH_TOKEN")

    @staticmethod
    def _create_download_link(fileId: str) -> str:
        return f"https://drive.google.com/uc?id={fileId}&export=download"

    @staticmethod
    def _create_folder_link(folderId: str) -> str:
        return f"https://drive.google.com/folderview?id={folderId}"

    def _create_token_file(self, code: Optional[str] = None) -> Any:
        flow = InstalledAppFlow.from_client_config(
            self.client_secrets,
            self.gdrive_creds["oauth_scope"],
            redirect_uri="http://localhost:8080/",
        )
        if not code:
            auth_url, _ = flow.authorization_url(prompt="consent")
            return auth_url

        try:
            flow.fetch_token(code=code)
            self.creds = flow.credentials
            if self.creds:
                with open(self.token_file, "w") as token:
                    token.write(self.creds.to_json())
                udB.set_key("GDRIVE_AUTH_TOKEN", self.creds.to_json())
            return True
        except Exception as e:
            return str(e)

    @property
    def _build(self) -> Any:
        if not self.creds or not self.creds.valid:
            return None
        return build("drive", "v2", credentials=self.creds, cache_discovery=False)

    def _set_permissions(self, fileId: str) -> None:
        _permissions = {
            "role": "reader",
            "type": "anyone",
            "value": None,
            "withLink": True,
        }
        service = self._build
        if service:
            service.permissions().insert(
                fileId=fileId, body=_permissions, supportsAllDrives=True
            ).execute()

    async def _upload_file(
        self,
        event: Any,
        path: str,
        filename: Optional[str] = None,
        folder_id: Optional[str] = None,
    ) -> Any:
        service = self._build
        if not service:
            raise Exception("Google Drive not authenticated.")
        last_txt = ""
        if not filename:
            filename = path.split("/")[-1]
        mime_type = guess_type(path)[0] or "application/octet-stream"
        media_body = MediaFileUpload(path, mimetype=mime_type, resumable=True)
        body: Dict[str, Any] = {
            "title": filename,
            "description": "Uploaded using Ultroid Userbot",
            "mimeType": mime_type,
        }
        if folder_id:
            body["parents"] = [{"id": folder_id}]
        elif self.folder_id:
            body["parents"] = [{"id": self.folder_id}]
        upload = service.files().insert(
            body=body, media_body=media_body, supportsAllDrives=True
        )
        start = time.time()
        _status = None
        while not _status:
            _progress, _status = upload.next_chunk(num_retries=3)
            if _progress:
                diff = time.time() - start
                completed = _progress.resumable_progress
                total_size = _progress.total_size
                percentage = round((completed / total_size) * 100, 2)
                speed = round(completed / diff, 2) if diff > 0 else 0
                eta = (
                    round((total_size - completed) / speed, 2) * 1000 if speed > 0 else 0
                )
                crnt_txt = (
                    f"`Uploading {filename} to GDrive...\n\n`"
                    f"`Status: {humanbytes(completed)}/{humanbytes(total_size)} »» {percentage}%\n`"
                    f"`Speed: {humanbytes(speed)}/s\n`"
                    f"`ETA: {time_formatter(eta)}`"
                )
                if round((diff % 10.00) == 0) or last_txt != crnt_txt:
                    await event.edit(crnt_txt)
                    last_txt = crnt_txt
        fileId = _status.get("id")
        try:
            self._set_permissions(fileId=fileId)
        except BaseException:
            pass
        _url = service.files().get(fileId=fileId, supportsAllDrives=True).execute()
        return _url.get("webContentLink")

    async def _download_file(
        self, event: Any, fileId: str, filename: Optional[str] = None
    ) -> Any:
        service = self._build
        if not service:
            return False, "Google Drive not authenticated."
        last_txt = ""
        if fileId.startswith("http"):
            if "=download" in fileId:
                fileId = fileId.split("=")[1].split("&")[0]
            elif "/view" in fileId:
                fileId = fileId.split("/")[-2]
        try:
            file_metadata = (
                service.files().get(fileId=fileId, supportsAllDrives=True).execute()
            )
            if not filename:
                filename = file_metadata["title"]
            downloader = service.files().get_media(
                fileId=fileId, supportsAllDrives=True
            )
        except Exception as ex:
            return False, str(ex)
        if not filename:
            return False, "Could not determine filename."
        with FileIO(filename, "wb") as file:
            start = time.time()
            download = MediaIoBaseDownload(file, downloader)
            _status = None
            while not _status:
                _progress, _status = download.next_chunk(num_retries=3)
                if _progress:
                    diff = time.time() - start
                    completed = _progress.resumable_progress
                    total_size = _progress.total_size
                    percentage = round((completed / total_size) * 100, 2)
                    speed = round(completed / diff, 2) if diff > 0 else 0
                    eta = (
                        round((total_size - completed) / speed, 2) * 1000
                        if speed > 0
                        else 0
                    )
                    crnt_txt = (
                        f"`Downloading {filename} from GDrive...\n\n`"
                        f"`Status: {humanbytes(completed)}/{humanbytes(total_size)} »» {percentage}%\n`"
                        f"`Speed: {humanbytes(speed)}/s\n`"
                        f"`ETA: {time_formatter(eta)}`"
                    )
                    if round((diff % 10.00) == 0) or last_txt != crnt_txt:
                        await event.edit(crnt_txt)
                        last_txt = crnt_txt
        return True, filename

    @property
    def _list_files(self) -> Dict[str, str]:
        service = self._build
        if not service:
            return {}
        _items = (
            service.files()
            .list(
                supportsTeamDrives=True,
                includeTeamDriveItems=True,
                spaces="drive",
                fields="nextPageToken, items(id, title, mimeType)",
                pageToken=None,
            )
            .execute()
        )
        _files = {}
        for files in _items.get("items", []):
            if files["mimeType"] == self.gdrive_creds["dir_mimetype"]:
                _files[self._create_folder_link(files["id"])] = files["title"]
            else:
                _files[self._create_download_link(files["id"])] = files["title"]
        return _files

    def create_directory(self, directory: str) -> Any:
        service = self._build
        if not service:
            return None
        body: Dict[str, Any] = {
            "title": directory,
            "mimeType": self.gdrive_creds["dir_mimetype"],
        }
        if self.folder_id:
            body["parents"] = [{"id": self.folder_id}]
        file = service.files().insert(body=body, supportsAllDrives=True).execute()
        fileId = file.get("id")
        self._set_permissions(fileId=fileId)
        return fileId

    def search(self, title: str) -> Dict[str, str]:
        service = self._build
        if not service:
            return {}
        query = f"title contains '{title}'"
        if self.folder_id:
            query = f"'{self.folder_id}' in parents and (title contains '{title}')"
        _items = (
            service.files()
            .list(
                supportsTeamDrives=True,
                includeTeamDriveItems=True,
                q=query,
                spaces="drive",
                fields="nextPageToken, items(id, title, mimeType)",
                pageToken=None,
            )
            .execute()
        )
        _files = {}
        for files in _items.get("items", []):
            _files[self._create_download_link(files["id"])] = files["title"]
        return _files

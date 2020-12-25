import urllib
from logging import Logger

import re
import requests

from cloudshell.cm.customscript.domain.cancellation_sampler import CancellationSampler
from cloudshell.cm.customscript.domain.script_file import ScriptFile
from cloudshell.cm.customscript.domain.script_configuration import ScriptConfiguration


class HttpAuth(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password


class ScriptDownloader(object):
    CHUNK_SIZE = 1024 * 1024

    def __init__(self, script_config, logger, cancel_sampler):
        """
        :type script_config: ScriptConfiguration
        :type logger: Logger
        :type cancel_sampler: CancellationSampler
        """
        self.script_config = script_config
        self.logger = logger
        self.cancel_sampler = cancel_sampler
        self.filename_pattern = "(?P<filename>\s*[\w,\s-]+\.(sh|bash|ps1)\s*)"
        self.filename_patterns = {
            "content-disposition": "\s*((?i)inline|attachment|extension-token)\s*;\s*filename=" + self.filename_pattern,
            "x-artifactory-filename": self.filename_pattern,
            "X-Gitlab-File-Name": self.filename_pattern
        }

    def download(self):
        """
        :type url: str
        :type auth: HttpAuth
        :rtype ScriptFile
        """
        gitlab_details = self.script_config.gitlab_details

        if not gitlab_details.server:
            # STANDARD FLOW
            script_repo = self.script_config.script_repo
            if script_repo.username and script_repo.password:
                auth = (script_repo.username, script_repo.password)
            else:
                auth = None
            self.logger.info("downloading script from url: {}".format(script_repo.url))
            response = requests.get(script_repo.url, auth=auth, stream=True, verify=False)
        else:
            # GITLAB REST API CALL
            url = "http://{}/api/v4/projects/{}/repository/files/{}/raw?ref={}".format(gitlab_details.server,
                                                                                       gitlab_details.project_id,
                                                                                       gitlab_details.script_path,
                                                                                       gitlab_details.script_branch)
            headers = {"PRIVATE-TOKEN": gitlab_details.access_token}
            self.logger.info("downloading script via Gitlab Rest call: {}".format(url))
            response = requests.get(url, stream=True, verify=False, headers=headers)

        self._validate_response_status_code(response)
        self._invalidate_gitlab_login_page(response.url, response.content)

        file_name = self._get_filename(response)
        file_txt = ''

        for chunk in response.iter_content(ScriptDownloader.CHUNK_SIZE):
            if chunk:
                file_txt += ''.join(chunk)
            self.cancel_sampler.throw_if_canceled()

        self._invalidate_html(file_txt)
        self.logger.info("file downloaded: {}".format(file_name))
        return ScriptFile(name=file_name, text=file_txt)

    def _validate_response_status_code(self, response):
        if response.status_code < 200 or response.status_code > 300:
            raise Exception('Failed to download script file: '+str(response.status_code)+' '+response.reason+
                            '. Please make sure the URL is valid, and the credentials are correct and necessary.')

    def _invalidate_html(self, content):
        if self._is_content_html(content):
            raise Exception('Failed to download script file: url points to an html file')

    def _invalidate_gitlab_login_page(self, response_url, content):
        if self._is_content_html(content) and "users/sign_in" in response_url:
            raise Exception('Authentication failed. Reached Gitlab Login. Gitlab Access Token required.')

    def _is_content_html(self, content):
        return content.lstrip('\n\r').lower().startswith('<!doctype html>')

    def _get_filename(self, response):

        # === search headers for file name ===
        for header_value, pattern in self.filename_patterns.iteritems():
            matching = re.match(pattern, response.headers.get(header_value, ""))
            if matching:
                file_name = matching.group('filename')
                if file_name:
                    return file_name.strip()

        # fallback, couldn't find file name from header, get it from url

        # === Github raw url search ===
        # ex. - https://raw.githubusercontent.com/QualiSystemsLab/App-Configuration-Demo-Scripts/master/allow_winrm.ps1
        file_name_from_url = urllib.unquote(response.url[response.url.rfind('/') + 1:])
        matching = re.match(self.filename_pattern, file_name_from_url)
        if matching:
            file_name = matching.group('filename')
            if file_name:
                return file_name.strip()

        # === Gitlab REST url search ===
        # ex. - 'http://192.168.85.62/api/v4/projects/2/repository/files/hello_world.sh/raw?ref=master'
        url_split = response.url.split("/")
        if url_split >= 2:
            file_name_from_url = url_split[-2]
            matching = re.match(self.filename_pattern, file_name_from_url)
            if matching:
                file_name = matching.group('filename')
                if file_name:
                    return file_name.strip()

        raise Exception("Script file of supported types: '.sh', '.bash', '.ps1' was not found")

import urllib
from logging import Logger

import re
import requests

from cloudshell.cm.customscript.domain.script_file import ScriptFile


class HttpAuth(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password


class ScriptDownloader(object):
    CHUNK_SIZE = 1024 * 1024

    def __init__(self, logger):
        """
        :type logger: Logger
        """
        self.logger = logger
        self.filename_pattern = "(?P<filename>\s*[\w,\s-]+\.(sh|bash|cmd|bat)\s*)"
        self.filename_patterns = {
            "content-disposition": "\s*((?i)inline|attachment|extension-token)\s*;\s*filename=" + self.filename_pattern,
            "x-artifactory-filename": self.filename_pattern
        }

    def download(self, url, auth):
        """
        :type url: str
        :type auth: HttpAuth
        :rtype ScriptFile
        """
        self.logger.info('Downloading file from \'%s\' ...' % url)
        response = requests.get(url, auth=(auth.username, auth.password) if auth else None, stream=True)
        file_name = self.get_filename.get_filename(response)
        file_txt = ''

        for chunk in response.iter_content(ScriptDownloader.CHUNK_SIZE):
            if chunk:
                file_txt += ''.join(chunk)

        return ScriptFile(name=file_name, text=file_txt)

    def get_filename(self, response):
        file_name = None
        for header_value, pattern in self.filename_patterns.iteritems():
            matching = re.match(pattern, response.headers.get(header_value, ""))
            if matching:
                file_name = matching.group('filename')
                break
        # fallback, couldn't find file name from header, get it from url
        if not file_name:
            file_name_from_url = urllib.unquote(response.url[response.url.rfind('/') + 1:])
            matching = re.match(self.filename_pattern, file_name_from_url)
            if matching:
                file_name = matching.group('filename')
        if not file_name:
            raise Exception("script file of supported types: '.sh', '.bash', '.cmd', or '.bat' was not found")
        return file_name.strip()
from unittest import TestCase
from cloudshell.cm.customscript.domain.gitlab_api_url_validator import is_gitlab_rest_url


class TestCustomScriptShell(TestCase):
    def test_http_url(self):
        input_url = "http://192.168.85.62/api/v4/projects/4/repository/files/hello_world.sh/raw?ref=master"
        is_gitlab = is_gitlab_rest_url(input_url)
        self.assertTrue(is_gitlab)

    def test_https_url(self):
        input_url = "https://192.168.85.62/api/v4/projects/4/repository/files/hello_world.sh/raw?ref=master"
        is_gitlab = is_gitlab_rest_url(input_url)
        self.assertTrue(is_gitlab)

    def test_broken_protocols_url(self):
        """ test that it fails with broken protocol"""
        input_url = "httpp://192.168.85.62/api/v4/projects/4/repository/files/hello_world.sh/raw?ref=master"
        # is_gitlab = is_gitlab_rest_url(input_url)
        with self.assertRaises(Exception) as context:
            is_gitlab_rest_url(input_url)
        self.assertTrue(context.exception)
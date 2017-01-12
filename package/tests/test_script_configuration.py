from unittest import TestCase

from cloudshell.cm.customscript.domain.script_configuration import ScriptConfigurationParser


class TestScriptConfiguration(TestCase):

    def test_cannot_parse_json_without_repository_details(self):
        json = '{}'
        with self.assertRaises(SyntaxError) as context:
            ScriptConfigurationParser.json_to_object(json)
        self.assertIn('Missing "repositoryDetails" node.', context.exception.message)

    def test_cannot_parse_json_without_repository_url(self):
        json = '{"repositoryDetails":{}}'
        with self.assertRaises(SyntaxError) as context:
            ScriptConfigurationParser.json_to_object(json)
        self.assertIn('Missing/Empty "repositoryDetails.url" node.', context.exception.message)

    def test_cannot_parse_json_with_an_empty_repository_url(self):
        json = '{"repositoryDetails":{"url":""}}'
        with self.assertRaises(SyntaxError) as context:
            ScriptConfigurationParser.json_to_object(json)
        self.assertIn('Missing/Empty "repositoryDetails.url" node.', context.exception.message)

    def test_cannot_parse_json_without_host_detalis(self):
        json = '{"repositoryDetails":{"url":"someurl"}}'
        with self.assertRaises(SyntaxError) as context:
            ScriptConfigurationParser.json_to_object(json)
        self.assertIn('Missing/Empty "hostDetails" node.', context.exception.message)

    def test_cannot_parse_json_with_an_empty_host_detalis(self):
        json = '{"repositoryDetails":{"url":"someurl"},"hostDetails":{}}'
        with self.assertRaises(SyntaxError) as context:
            ScriptConfigurationParser.json_to_object(json)
        self.assertIn('Missing/Empty "hostDetails" node.', context.exception.message)

    def test_cannot_parse_json_with_host_without_an_ip(self):
        json = '{"repositoryDetails":{"url":"someurl"},"hostDetails":{"someNode":""}}'
        with self.assertRaises(SyntaxError) as context:
            ScriptConfigurationParser.json_to_object(json)
        self.assertIn('Missing/Empty "hostDetails.ip" node.', context.exception.message)

    def test_cannot_parse_json_with_host_with_an_empty_ip(self):
        json = '{"repositoryDetails":{"url":"someurl"},"hostDetails":{"ip":""}}'
        with self.assertRaises(SyntaxError) as context:
            ScriptConfigurationParser.json_to_object(json)
        self.assertIn('Missing/Empty "hostDetails.ip" node.', context.exception.message)

    def test_cannot_parse_json_with_host_without_an_connection_method(self):
        json = '{"repositoryDetails":{"url":"someurl"},"hostDetails":{"ip":"x.x.x.x"}}'
        with self.assertRaises(SyntaxError) as context:
            ScriptConfigurationParser.json_to_object(json)
        self.assertIn('Missing/Empty "hostDetails.connectionMethod" node.', context.exception.message)

    def test_cannot_parse_json_with_host_with_an_empty_connection_method(self):
        json = '{"repositoryDetails":{"url":"someurl"},"hostDetails":{"ip":"x.x.x.x", "connectionMethod":""}}'
        with self.assertRaises(SyntaxError) as context:
            ScriptConfigurationParser.json_to_object(json)
        self.assertIn('Missing/Empty "hostDetails.connectionMethod" node.', context.exception.message)
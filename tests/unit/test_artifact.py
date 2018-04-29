from unittest import TestCase
import logging
import os
import six

try:
    from mock import MagicMock, patch, mock_open
except ImportError:
    from unittest.mock import MagicMock, patch, mock_open

from repositorytools import LocalArtifact, LocalArtifactWithPom


class ArtifactTest(TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def test_detect_name_ver_ext(self):
        artifacts = {
            'my_local_path/devbox-2.0.0.tgz': ('devbox', '2.0.0', 'tgz'),
            'my_local_path/python-foo2-2.3.4.ext': ('python-foo2', '2.3.4', 'ext'),
            'my_local_path/infra-6.6-4.tgz': ('infra', '6.6-4', 'tgz'),
            'my_local_path/update-hostname-0.1.4-1.el6.noarch.rpm': ('update-hostname', '0.1.4-1.el6.noarch', 'rpm'),
            'my_local_path/test-1.0.txt': ('test', '1.0', 'txt')
        }

        for local_path, nameverext in six.iteritems(artifacts):
            expected_name, expected_version, expected_extension = nameverext
            local_artifact = LocalArtifact('com.fooware', local_path=local_path)

            self.assertEqual(expected_name, local_artifact.artifact)
            self.assertEqual(expected_version, local_artifact.version)
            self.assertEqual(expected_extension, local_artifact.extension)

class LocalArtifactWithPomTest(TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.patch_os = patch('os.path.exists', return_value=True)
        self.patch_os.start()
        self.addCleanup(self.patch_os.stop)

    def test_pom_filename(self):
        with patch('repositorytools.lib.artifact.LocalArtifactWithPom.detect_from_pom', return_value=(None, None, None, None, None)):
            artifact = LocalArtifactWithPom('my_local_path/devbox-2.0.0.jar')
            self.assertEqual(artifact._pom_local_path(), 'my_local_path/devbox-2.0.0.pom')

    def test_pom_file_to_dict_raises_on_invalid_data(self):
        with patch('builtins.open', mock_open(read_data='garbage')):
            with self.assertRaises(ValueError):
                artifact = LocalArtifactWithPom('.')

    def test_pom_file_to_dict_parses_pom(self):
        artifact = LocalArtifactWithPom(os.path.join(os.path.dirname(__file__), 'neo4j.jar'))
        self.assertEqual(str(artifact), 'org.neo4j:neo4j-cypher-compiler-2.1:2.1.2:jdk15:jar')

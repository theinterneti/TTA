# Logseq: [[TTA.dev/Tests/Helpers/Neo4j]]
from unittest.mock import Mock


def build_mock_driver():
    mock_driver = Mock()
    mock_session_ctx = Mock()
    mock_session = Mock()
    mock_session_ctx.__enter__.return_value = mock_session
    mock_session_ctx.__exit__.return_value = None
    mock_driver.session.return_value = mock_session_ctx
    mock_session.run.return_value = Mock(single=Mock(return_value=None))
    return mock_driver

import pytest
from click.testing import CliRunner
from unittest.mock import patch
import check_site

@pytest.mark.parametrize("url, expected_output", [
    ("http://example.com", 
     "--\nSite Status - Online\nStatus Code - 200\n--\nDNS Information\n--\nIP: 93.184.216.34"),
    ("http://www.example.com",
     "--\nSite Status - Offline")
])
def test_check_site(url, expected_output):
    runner = CliRunner()
    with patch('requests.get') as mock_get, \
         patch('socket.gethostbyname') as mock_gethostbyname, \
         patch('dns.resolver.resolve') as mock_resolve:

        mock_response = mock_get.return_value
        mock_response.status_code = 200 if url == "http://example.com" else 404
        if url == "http://example.com":
            mock_response.headers = {'Location': 'http://www.example.com'}

        mock_gethostbyname.return_value = '93.184.216.34'
        mock_resolve.return_value.__iter__.return_value = ['example.com']

        result = runner.invoke(check_site.check_site, [url])
        assert result.exit_code == 0
        assert result.output.strip() == expected_output.strip()


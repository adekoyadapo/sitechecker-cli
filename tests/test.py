import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock
import check_site


@pytest.mark.parametrize("url, status_code, headers, dns_ip, cname, expected_output", [
    ("http://example.com", 200, 
     {'Server': 'Apache', 'Date': 'Sat, 14 Dec 2024 12:00:00 GMT', 'Content-Type': 'text/html'},
     '93.184.216.34', None, 
     "--\nSite Status - Online\nStatus Code - 200\n--\nHTTP Headers\n--\nServer: Apache\nDate: Sat, 14 Dec 2024 12:00:00 GMT\nContent-Type: text/html\n--\nDNS Information\n--\nIP: 93.184.216.34\nCNAME: Not Found\nMail Servers: Not Found\nName Servers: Not Found"),
    ("http://www.example.com", 404, {}, None, None, 
     "--\nSite Status - Offline\nStatus Code - 404"),
    ("http://unavailable-site.com", None, {}, None, None, 
     "--\nSite Status - Unavailable\nError: Unable to connect to http://unavailable-site.com.")
])
def test_check_site(url, status_code, headers, dns_ip, cname, expected_output):
    runner = CliRunner()
    with patch('requests.get') as mock_get, \
         patch('socket.gethostbyname') as mock_gethostbyname, \
         patch('dns.resolver.resolve') as mock_resolve:

        # Mock the requests.get behavior
        if status_code:
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_response.headers = headers
            mock_get.return_value = mock_response
        else:
            mock_get.side_effect = Exception("Unable to connect")

        # Mock DNS information
        mock_gethostbyname.return_value = dns_ip if dns_ip else Exception("DNS resolution failed")
        
        if cname:
            mock_resolve.return_value.__iter__.return_value = [Mock(target=Mock(to_text=lambda: cname))]
        else:
            mock_resolve.side_effect = Exception("CNAME not found")

        # Invoke the command
        result = runner.invoke(check_site.check_site, [url])

        # Assert the output
        assert result.exit_code == 0
        assert result.output.strip() == expected_output.strip()
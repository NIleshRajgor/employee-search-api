import unittest
import json
from unittest.mock import patch
from collections import defaultdict
from app.common import limit_utils
from app.common.constant import MAX_REQUESTS
from pathlib import Path

class TestRateLimiter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        json_path = Path(__file__).parent.parent / "mock_response/test_limit_data.json"
        with open(json_path) as f:
            cls.test_data = json.load(f)

    def setUp(self):
        limit_utils.request_log = defaultdict(list)

    @patch('time.time', return_value=1000.0)
    def test_allows_requests_below_limit(self, mock_time):
        data = self.test_data["below_limit"]
        for _ in range(data["requests"]):
            self.assertFalse(limit_utils.is_rate_limited(data["org_id"], data["ip"]))

    @patch('time.time', return_value=1000.0)
    def test_blocks_requests_above_limit(self, mock_time):
        data = self.test_data["above_limit"]
        for _ in range(data["requests"]):
            self.assertFalse(limit_utils.is_rate_limited(data["org_id"], data["ip"]))
        self.assertTrue(limit_utils.is_rate_limited(data["org_id"], data["ip"]))

    @patch('time.time')
    def test_resets_after_window_expires(self, mock_time):
        data = self.test_data["window_expiry"]
        mock_time.side_effect = data["timestamps"]

        self.assertFalse(limit_utils.is_rate_limited(data["org_id"], data["ip"]))
        self.assertFalse(limit_utils.is_rate_limited(data["org_id"], data["ip"]))
        self.assertFalse(limit_utils.is_rate_limited(data["org_id"], data["ip"]))
        self.assertFalse(limit_utils.is_rate_limited(data["org_id"], data["ip"]))

    @patch('time.time', return_value=1000.0)
    def test_separate_keys_are_tracked_independently(self, mock_time):
        for entry in self.test_data["separate_keys"]:
            self.assertFalse(limit_utils.is_rate_limited(entry["org_id"], entry["ip"]))

    @patch('time.time', return_value=1000.0)
    def test_exact_limit_allowed(self, mock_time):
        org_id = 'orgX'
        ip = '9.9.9.9'

        for _ in range(MAX_REQUESTS):
            self.assertFalse(limit_utils.is_rate_limited(org_id, ip))

        self.assertTrue(limit_utils.is_rate_limited(org_id, ip))


if __name__ == '__main__':
    unittest.main()

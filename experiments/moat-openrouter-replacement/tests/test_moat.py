import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from moat.router import LLMProvider, MoatRouter

class TestMoatRouter(unittest.TestCase):
    
    @patch('requests.post')
    def test_fallback_strategy_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "Hello from mock!"}}]}
        mock_post.return_value = mock_response

        router = MoatRouter(strategy="fallback")
        p1 = LLMProvider("prov1", "http://api.prov1.com/v1")
        router.add_provider(p1)

        res = router.route_chat({"model": "gpt-4", "messages": []})
        self.assertEqual(res["choices"][0]["message"]["content"], "Hello from mock!")
        self.assertTrue(p1.is_healthy)

    @patch('requests.post')
    def test_fallback_strategy_failover(self, mock_post):
        # First provider fails, second succeeds
        fail_response = MagicMock()
        fail_response.status_code = 500
        fail_response.text = "Internal Error"

        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {"choices": [{"message": {"content": "Fallback success"}}]}

        mock_post.side_effect = [fail_response, success_response]

        router = MoatRouter(strategy="fallback")
        p1 = LLMProvider("failing-prov", "http://api.fail.com/v1")
        p2 = LLMProvider("backup-prov", "http://api.backup.com/v1")
        router.add_provider(p1)
        router.add_provider(p2)

        res = router.route_chat({"model": "gpt-4", "messages": []})
        self.assertEqual(res["choices"][0]["message"]["content"], "Fallback success")
        self.assertFalse(p1.is_healthy)
        self.assertTrue(p2.is_healthy)

    def test_no_providers_raises_error(self):
        router = MoatRouter(strategy="fallback")
        with self.assertRaises(ValueError):
            router.route_chat({"model": "gpt-4", "messages": []})

if __name__ == '__main__':
    unittest.main()

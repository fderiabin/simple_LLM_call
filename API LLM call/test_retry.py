import unittest
from unittest.mock import MagicMock, patch
from retry import with_retry


def make_fake_response(status_code):
    """Helper to create a mock response with a given status code."""
    #MagicMock simulates the behavior of nearly any object. In this case we want to append attributes like status_code,
    #ok, and text to our mock response object.
    resp = MagicMock()
    resp.status_code = status_code
    resp.ok = (200 <= status_code < 300)
    resp.text = f"fake {status_code} body"
    return resp


class TestRetry(unittest.TestCase):

    def test_success_on_first_try(self):
        """No retries needed when the request succeeds immediately."""
        request_func = MagicMock(return_value=make_fake_response(200))

        result = with_retry(request_func, max_retries=3, base_delay=0.01)

        self.assertTrue(result.ok)
        self.assertEqual(request_func.call_count, 1)

    @patch("retry.time.sleep")  # don't actually wait during tests
    def test_retries_then_succeeds(self, mock_sleep):
        """Retries on 503 twice, then succeeds on third attempt."""
        request_func = MagicMock(side_effect=[
            make_fake_response(503),
            make_fake_response(503),
            make_fake_response(200),
        ])

        result = with_retry(request_func, max_retries=3, base_delay=1.0)

        self.assertTrue(result.ok)
        self.assertEqual(request_func.call_count, 3)
        # Check exponential delays: 1s, 2s
        mock_sleep.assert_any_call(1.0)
        mock_sleep.assert_any_call(2.0)

    @patch("retry.time.sleep")
    def test_exhausts_all_retries(self, mock_sleep):
        """Raises after all retries are used up."""
        request_func = MagicMock(return_value=make_fake_response(429))

        with self.assertRaises(Exception):
            with_retry(request_func, max_retries=2, base_delay=0.01)

        # 1 initial + 2 retries = 3 calls total
        self.assertEqual(request_func.call_count, 3)

    def test_non_retryable_error_fails_immediately(self):
        """A 401 should not be retried — fail right away."""
        request_func = MagicMock(return_value=make_fake_response(401))

        with self.assertRaises(Exception):
            with_retry(request_func, max_retries=3, base_delay=0.01)

        self.assertEqual(request_func.call_count, 1)

    @patch("retry.time.sleep")
    def test_rate_limit_429_is_retried(self, mock_sleep):
        """429 (rate limit) should be retried, not crash immediately."""
        request_func = MagicMock(side_effect=[
            make_fake_response(429),
            make_fake_response(200),
        ])

        result = with_retry(request_func, max_retries=3, base_delay=1.0)

        self.assertTrue(result.ok)
        self.assertEqual(request_func.call_count, 2)


if __name__ == "__main__":
    unittest.main()
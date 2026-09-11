import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rion_wechat_reader as reader


class NotificationPayloadTest(unittest.TestCase):
    def test_nested_request_fields_are_supported(self):
        payload = {
            "req": {"titl": "sender", "body": "message body"},
        }
        title, body = reader.notification_title_body(payload)
        self.assertEqual(title, "sender")
        self.assertEqual(body, "message body")

    def test_top_level_fields_remain_supported(self):
        payload = {"titl": "sender", "body": "message body"}
        self.assertEqual(reader.notification_title_body(payload), ("sender", "message body"))


if __name__ == "__main__":
    unittest.main()

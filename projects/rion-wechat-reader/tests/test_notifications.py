import unittest
from pathlib import Path
import sys
import json
import stat
import tempfile
from unittest import mock

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

    def test_event_id_is_stable_and_distinguishes_records(self):
        first = reader.notification_event_id(b"one", 123, "sender", "body")
        self.assertEqual(first, reader.notification_event_id(b"one", 123, "sender", "body"))
        self.assertNotEqual(first, reader.notification_event_id(b"two", 123, "sender", "body"))

    def test_watch_persists_private_state_and_deduplicates(self):
        record = {
            "event_id": "event-1",
            "sender": "sender",
            "chat": "sender",
            "text": "message body",
            "content": "message body",
            "create_time": 123,
            "time": "1970-01-01T00:02:03+00:00",
            "source": "macos_notification_preview",
            "coverage": "incoming_preview_only",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "private"
            state = root / "state.json"
            output = root / "events.jsonl"
            with mock.patch.object(reader, "notification_records", return_value=[record]):
                first = reader.notification_watch(0, 1, 10, state, output, True)
                second = reader.notification_watch(0, 1, 10, state, output, True)
            self.assertEqual(first["captured"], 1)
            self.assertEqual(second["captured"], 0)
            self.assertEqual(len(output.read_text(encoding="utf-8").splitlines()), 1)
            self.assertEqual(json.loads(state.read_text(encoding="utf-8"))["seen_event_ids"], ["event-1"])
            self.assertEqual(stat.S_IMODE(root.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(state.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)


if __name__ == "__main__":
    unittest.main()

import importlib
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from config import Config


OPERATIONS = [
    ("read", "GET", "/api/conversations/{id}", None),
    ("update", "PUT", "/api/conversations/{id}", {"title": "Changed", "archive": True}),
    ("delete", "DELETE", "/api/conversations/{id}", None),
    ("chat", "POST", "/api/chat", {"session_id": "{id}", "message": "Hello"}),
    ("multimodal", "POST", "/api/multimodal", {"session_id": "{id}", "message": "Hello", "image": "aGVsbG8="}),
    ("vision", "POST", "/api/vision/quick", {"session_id": "{id}", "image": "aGVsbG8="}),
    ("screenshot", "POST", "/api/screenshots", {"conversation_id": "{id}", "image": "aGVsbG8="}),
]


class ConversationOwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.config = patch.multiple(
            Config,
            DATABASE_PATH=str(Path(cls.directory.name) / "test.db"),
            SCREENSHOT_DIR=str(Path(cls.directory.name) / "screenshots"),
        )
        cls.config.start()
        try:
            cls.module = importlib.import_module("app")
        except Exception:
            cls.config.stop()
            cls.directory.cleanup()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.config.stop()
        cls.directory.cleanup()

    def setUp(self):
        self.module.app.config["TESTING"] = True
        self.client = self.module.app.test_client()
        database = importlib.import_module("services.database")
        with closing(database.get_db()) as connection:
            connection.executescript("DELETE FROM screenshots; DELETE FROM messages; DELETE FROM conversations; DELETE FROM users;")
            connection.commit()
        self.owner = database.create_user("owner", "unused-test-hash")
        self.other = database.create_user("other", "unused-test-hash")
        self.conversation = "owned-conversation"
        database.create_conversation(self.conversation, self.owner, "Original")
        database.add_message(self.conversation, "user", "Private original message")
        self.before = database.get_conversation(self.conversation)
        self.messages_before = database.get_conversation_messages(self.conversation)
        self.database = database
        cost = importlib.import_module("services.cost_control")
        self.rate_limits = patch.dict(cost._rate_limit_store, {}, clear=True)
        self.rate_limits.start()
        self.addCleanup(self.rate_limits.stop)
        self.external = {}
        for name, result in [("chat", "Test reply"), ("analyze_frame", "Test description"), ("describe_scene", "Test scene")]:
            mock = patch.object(self.module, name, return_value=result)
            self.external[name] = mock.start()
            self.addCleanup(mock.stop)
        self.files_before = set(Path(Config.SCREENSHOT_DIR).iterdir())

    def request(self, operation, identity, conversation=None):
        _, method, path, body = operation
        conversation = conversation or self.conversation
        headers = {}
        if identity is not None:
            with self.module.app.app_context():
                token = self.module.create_access_token(identity=str(identity))
            headers["Authorization"] = "Bearer " + token
        payload = None if body is None else {
            key: value.replace("{id}", conversation) if isinstance(value, str) else value
            for key, value in body.items()
        }
        return self.client.open(path.format(id=conversation), method=method, json=payload, headers=headers)

    def assert_no_side_effects(self):
        self.assertEqual(self.database.get_conversation(self.conversation), self.before)
        self.assertEqual(self.database.get_conversation_messages(self.conversation), self.messages_before)
        self.assertEqual(self.database.get_user_screenshots(self.owner), [])
        self.assertEqual(self.database.get_user_screenshots(self.other), [])
        self.assertEqual(set(Path(Config.SCREENSHOT_DIR).iterdir()), self.files_before)
        for mock in self.external.values():
            mock.assert_not_called()

    def test_optional_vision_without_conversation_still_works(self):
        operation = ("vision", "POST", "/api/vision/quick", {"image": "aGVsbG8="})
        response = self.request(operation, self.owner)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["result"], "Test scene")

    def test_optional_screenshot_without_conversation_still_works(self):
        operation = ("screenshot", "POST", "/api/screenshots", {"image": "aGVsbG8="})
        response = self.request(operation, self.owner)
        self.assertEqual(response.status_code, 200)
        record = self.database.get_user_screenshots(self.owner)[0]
        self.assertIsNone(record["conversation_id"])

    def screenshot_fixture(self):
        filename = "private-fixture.jpg"
        (Path(Config.SCREENSHOT_DIR) / filename).write_bytes(b"private image fixture")
        self.database.add_screenshot(self.owner, filename, "Private", self.conversation)
        return ("image", "GET", "/api/screenshots/" + filename, None)

    def test_screenshot_download_requires_login(self):
        response = self.request(self.screenshot_fixture(), None)
        self.assertEqual(response.status_code, 401)

    def test_screenshot_download_rejects_other_users(self):
        response = self.request(self.screenshot_fixture(), self.other)
        self.assertEqual(response.status_code, 404)

    def test_screenshot_download_allows_owner(self):
        response = self.request(self.screenshot_fixture(), self.owner)
        self.addCleanup(response.close)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"private image fixture")

    def test_screenshot_download_rejects_parent_directory_paths(self):
        operation = ("image", "GET", "/api/screenshots/../test.db", None)
        response = self.request(operation, self.owner)
        self.addCleanup(response.close)
        self.assertEqual(response.status_code, 404)

    def test_screenshot_download_rejects_unrecorded_files(self):
        (Path(Config.SCREENSHOT_DIR) / "orphan.jpg").write_bytes(b"orphan fixture")
        response = self.request(("image", "GET", "/api/screenshots/orphan.jpg", None), self.owner)
        self.addCleanup(response.close)
        self.assertEqual(response.status_code, 404)


def ownership_test(operation, identity_kind):
    def check(self):
        identity = {"owner": self.owner, "foreign": self.other, "missing": self.owner, "anonymous": None}[identity_kind]
        conversation = "missing-conversation" if identity_kind == "missing" else self.conversation
        response = self.request(operation, identity, conversation)
        if identity_kind in ("foreign", "missing"):
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, {"error": "会话不存在"})
            self.assert_no_side_effects()
        elif identity_kind == "anonymous":
            self.assertEqual(response.status_code, 401)
            self.assert_no_side_effects()
        else:
            self.assertEqual(response.status_code, 200)
            action = operation[0]
            if action == "read":
                self.assertEqual(response.json["messages"][0]["content"], "Private original message")
            elif action == "update":
                record = self.database.get_conversation(self.conversation)
                self.assertEqual((record["title"], record["is_archived"]), ("Changed", 1))
            elif action == "delete":
                self.assertIsNone(self.database.get_conversation(self.conversation))
                self.assertEqual(self.database.get_conversation_messages(self.conversation), [])
            elif action in ("chat", "multimodal", "vision"):
                messages = self.database.get_conversation_messages(self.conversation)
                self.assertEqual(len(messages), 3)
                self.assertEqual(messages[-1]["role"], "assistant")
            elif action == "screenshot":
                record = self.database.get_user_screenshots(self.owner)[0]
                self.assertEqual(record["conversation_id"], self.conversation)
    return check


for operation in OPERATIONS:
    for identity_kind in ("owner", "foreign", "missing", "anonymous"):
        setattr(ConversationOwnershipTests, f"test_{identity_kind}_{operation[0]}", ownership_test(operation, identity_kind))


if __name__ == "__main__":
    unittest.main()

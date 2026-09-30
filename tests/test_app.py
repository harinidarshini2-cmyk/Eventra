import unittest

from app import app


class EventraTestCase(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_events_api(self):
        response = self.client.get("/api/events")
        self.assertEqual(response.status_code, 200)

    def test_event_not_found(self):
        response = self.client.get("/api/events/99999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()

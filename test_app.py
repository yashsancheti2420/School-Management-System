"""Basic smoke tests used locally and by GitHub Actions."""
import unittest

from app import app


class SchoolSphereTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_public_pages_are_available(self):
        paths = ("/", "/students", "/teachers", "/staff", "/classes", "/subjects", "/reports", "/health")
        for path in paths:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)


if __name__ == "__main__":
    unittest.main()

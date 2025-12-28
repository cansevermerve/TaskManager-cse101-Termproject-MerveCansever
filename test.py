import os
import tempfile
import unittest
from datetime import datetime, timedelta

from storage import save_state, load_state, backup_state
from activity import productivity_stats


class TaskTests(unittest.TestCase):
    def test_productivity_stats_completed(self):
        tasks = [
            {
                "id": "1",
                "title": "Task 1",
                "description": "",
                "category": "School",
                "priority": "High",
                "status": "completed",
                "due_date": "2025-01-10",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-05T00:00:00",
                "subtasks": []
            }
        ]
        activity_log = []
        stats = productivity_stats(tasks, activity_log)
        self.assertEqual(stats["tasks_completed"], 1)
        self.assertIn("School", stats["category_trends"])


class StorageTests(unittest.TestCase):
    def test_backup_and_load_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = os.path.join(tmp, "data")
            backup_dir = os.path.join(tmp, "backups")

            tasks = [
                {
                    "id": "1",
                    "title": "Task 1",
                    "description": "",
                    "category": "Test",
                    "priority": "Low",
                    "status": "pending",
                    "due_date": "2025-01-10",
                    "created_at": "2025-01-01T00:00:00",
                    "updated_at": "2025-01-01T00:00:00",
                    "subtasks": []
                }
            ]
            categories = []
            activity_log = []

            save_state(base_dir, tasks, categories, activity_log)
            backups = backup_state(base_dir, backup_dir)

            self.assertTrue(os.path.exists(backups[0]))

            loaded_tasks, loaded_categories, loaded_log = load_state(base_dir)
            self.assertEqual(len(loaded_tasks), 1)
            self.assertEqual(loaded_tasks[0]["title"], "Task 1")


if __name__ == "__main__":
    unittest.main()

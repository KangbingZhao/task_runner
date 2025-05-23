import unittest
from unittest.mock import patch, MagicMock
import importlib
import sys

class SchedulerCoreTest(unittest.TestCase):
    @patch('core.scheduler.CronTrigger')
    @patch('core.scheduler.BackgroundScheduler')
    @patch('core.scheduler.TaskLog')
    def test_task_registration_and_run(self, mock_TaskLog, mock_BackgroundScheduler, mock_CronTrigger):
        from core import scheduler
        fake_config = {
            'mock_task': {
                'enabled': True,
                'cron': '0 0 * * *',
                'description': '测试任务'
            }
        }
        sys.modules['tasks.mock_task'] = MagicMock(run=MagicMock())
        mock_logger = MagicMock()
        scheduler.register_tasks(mock_BackgroundScheduler.return_value, mock_logger, fake_config)
        self.assertTrue(mock_BackgroundScheduler.return_value.add_job.called)
        self.assertTrue(mock_logger.info.called)

if __name__ == "__main__":
    unittest.main()

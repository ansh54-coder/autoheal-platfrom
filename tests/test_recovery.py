
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from controller.recovery_engine import RecoveryEngine


class RecoveryTests(unittest.TestCase):

    def setUp(self):

        self.api = Mock()

        self.pod = SimpleNamespace(
            metadata=SimpleNamespace(
                name="autoheal-pod-1",
                labels={
                    "app": "autoheal"
                }
            )
        )

    def test_deletes_matching_pod(self):

        engine = RecoveryEngine(
            self.api,
            namespace="default"
        )

        result = engine.recover(
            self.pod,
            "test failure"
        )

        self.assertTrue(result)

        self.api.delete_namespaced_pod.assert_called_once_with(
            name="autoheal-pod-1",
            namespace="default",
            grace_period_seconds=5
        )

    def test_dry_run_does_not_delete(self):

        engine = RecoveryEngine(
            self.api,
            dry_run=True
        )

        result = engine.recover(
            self.pod,
            "test failure"
        )

        self.assertFalse(result)

        self.api.delete_namespaced_pod.assert_not_called()

    def test_refuses_wrong_label(self):

        self.pod.metadata.labels = {
            "app": "other"
        }

        engine = RecoveryEngine(
            self.api
        )

        result = engine.recover(
            self.pod,
            "test failure"
        )

        self.assertFalse(result)

        self.api.delete_namespaced_pod.assert_not_called()


if __name__ == "__main__":
    unittest.main()


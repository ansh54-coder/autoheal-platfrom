
import unittest
from types import SimpleNamespace

from controller.detector import FailureDetector


def create_pod(name, ready, phase="Running"):

    condition = SimpleNamespace(
        type="Ready",
        status="True" if ready else "False"
    )

    return SimpleNamespace(
        metadata=SimpleNamespace(
            name=name
        ),

        status=SimpleNamespace(
            phase=phase,
            conditions=[condition]
        )
    )


class DetectorTests(unittest.TestCase):

    def test_ready_pod_not_detected(self):

        detector = FailureDetector(
            unready_grace_seconds=10
        )

        result = detector.detect(
            [create_pod("pod-1", True)],
            now=100
        )

        self.assertEqual(result, [])

    def test_unready_pod_detected_after_grace(self):

        detector = FailureDetector(
            unready_grace_seconds=10
        )

        pod = create_pod(
            "pod-1",
            False
        )

        first_result = detector.detect(
            [pod],
            now=100
        )

        self.assertEqual(
            first_result,
            []
        )

        second_result = detector.detect(
            [pod],
            now=111
        )

        self.assertEqual(
            len(second_result),
            1
        )

    def test_failed_pod_detected_immediately(self):

        detector = FailureDetector()

        pod = create_pod(
            "pod-1",
            False,
            phase="Failed"
        )

        result = detector.detect(
            [pod],
            now=100
        )

        self.assertEqual(
            len(result),
            1
        )


if __name__ == "__main__":
    unittest.main()

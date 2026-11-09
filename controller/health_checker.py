
from detector import FailureDetector


class HealthChecker:

    @staticmethod
    def pod_is_ready(pod):
        return FailureDetector.is_ready(pod)

    @staticmethod
    def summarize(pods):

        total = len(pods)

        ready = sum(
            1
            for pod in pods
            if FailureDetector.is_ready(pod)
        )

        return {
            "total": total,
            "ready": ready,
            "unready": total - ready
        }


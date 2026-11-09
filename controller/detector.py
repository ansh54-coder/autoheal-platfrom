
import time


class FailureDetector:

    def __init__(self, unready_grace_seconds=30):
        self.grace = unready_grace_seconds
        self.first_unready = {}

    @staticmethod
    def is_ready(pod):
        conditions = getattr(
            pod.status,
            "conditions",
            None
        ) or []

        return any(
            condition.type == "Ready"
            and condition.status == "True"
            for condition in conditions
        )

    def detect(self, pods, now=None):
        now = now or time.time()

        unhealthy = []
        current_names = set()

        for pod in pods:

            name = pod.metadata.name
            current_names.add(name)

            phase = getattr(
                pod.status,
                "phase",
                None
            )

            if phase == "Failed":

                unhealthy.append(
                    (pod, "Pod phase is Failed")
                )

                self.first_unready.pop(name, None)
                continue

            if self.is_ready(pod):

                self.first_unready.pop(name, None)
                continue

            started = self.first_unready.setdefault(
                name,
                now
            )

            if now - started >= self.grace:

                unhealthy.append(
                    (
                        pod,
                        f"Pod not Ready for {self.grace} seconds"
                    )
                )

        stale_names = (
            set(self.first_unready) - current_names
        )

        for name in stale_names:
            self.first_unready.pop(name, None)

        return unhealthy


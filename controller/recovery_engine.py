
import logging


logger = logging.getLogger(__name__)


class RecoveryEngine:

    def __init__(
        self,
        core_api,
        namespace="default",
        dry_run=False
    ):

        self.core_api = core_api
        self.namespace = namespace
        self.dry_run = dry_run

    def recover(self, pod, reason):

        name = pod.metadata.name

        logger.warning(
            "Recovery requested for pod=%s reason=%s",
            name,
            reason
        )

        if self.dry_run:

            logger.warning(
                "DRY RUN: Would delete pod %s",
                name
            )

            return False

        labels = pod.metadata.labels or {}

        # Safety check: only recover AutoHeal pods.
        if labels.get("app") != "autoheal":

            logger.error(
                "Refusing to delete pod %s: unexpected labels",
                name
            )

            return False

        self.core_api.delete_namespaced_pod(
            name=name,
            namespace=self.namespace,
            grace_period_seconds=5
        )

        logger.info(
            "Deleted unhealthy pod %s",
            name
        )

        return True



import logging
import os
import time

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

from detector import FailureDetector
from recovery_engine import RecoveryEngine
from health_checker import HealthChecker


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger("autoheal-controller")


NAMESPACE = os.getenv(
    "NAMESPACE",
    "default"
)

LABEL_SELECTOR = os.getenv(
    "LABEL_SELECTOR",
    "app=autoheal"
)

POLL_SECONDS = int(
    os.getenv("POLL_SECONDS", "10")
)

UNREADY_GRACE_SECONDS = int(
    os.getenv("UNREADY_GRACE_SECONDS", "30")
)

DRY_RUN = (
    os.getenv("DRY_RUN", "false").lower() == "true"
)


def load_kubernetes_config():

    try:

        config.load_incluster_config()

        logger.info(
            "Loaded in-cluster Kubernetes configuration"
        )

    except config.ConfigException:

        config.load_kube_config()

        logger.info(
            "Loaded local Kubernetes configuration"
        )


def main():

    load_kubernetes_config()

    core_api = client.CoreV1Api()

    detector = FailureDetector(
        UNREADY_GRACE_SECONDS
    )

    recovery = RecoveryEngine(
        core_api,
        namespace=NAMESPACE,
        dry_run=DRY_RUN
    )

    logger.info(
        "Controller started. Namespace=%s Selector=%s",
        NAMESPACE,
        LABEL_SELECTOR
    )

    while True:

        try:

            pods = core_api.list_namespaced_pod(
                namespace=NAMESPACE,
                label_selector=LABEL_SELECTOR
            ).items

            health = HealthChecker.summarize(
                pods
            )

            logger.info(
                "Pod health: %s",
                health
            )

            unhealthy_pods = detector.detect(
                pods
            )

            for pod, reason in unhealthy_pods:

                try:

                    recovery.recover(
                        pod,
                        reason
                    )

                except ApiException as error:

                    logger.error(
                        "Kubernetes API error: %s",
                        error
                    )

        except ApiException as error:

            logger.error(
                "Unable to list pods: %s",
                error
            )

        except Exception:

            logger.exception(
                "Unexpected controller error"
            )

        time.sleep(
            POLL_SECONDS
        )


if __name__ == "__main__":
    main()


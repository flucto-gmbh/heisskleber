# /// script
# dependencies = [
#   "pyzmq",
#   "heisskleber"
# ]
# ///

import argparse
import logging
import sys

import zmq

from heisskleber.zmq import ZmqConf

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - ZmqBroker - %(levelname)s - %(message)s")


def main() -> None:
    """Run ZMQ broker."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, required=True, help="ZMQ configuration file (yaml or json)")

    args = parser.parse_args()

    config = ZmqConf.from_file(args.config)

    try:
        ctx = zmq.Context()

        logger.info("Creating XPUB socket")
        xpub = ctx.socket(zmq.XPUB)
        logger.info("Creating XSUB socket")
        xsub = ctx.socket(zmq.XSUB)

        logger.info("Connecting XPUB socket to %(addr)s", {"addr": config.subscriber_address})
        xpub.bind(config.subscriber_address)

        logger.info("Connecting XSUB socket to %(addr)s", {"addr": config.publisher_address})
        xsub.bind(config.publisher_address)

        logger.info("Starting proxy...")
        zmq.proxy(xpub, xsub)
    except Exception:
        logger.exception("Oh no! ZMQ broker failed!")
        sys.exit(-1)


if __name__ == "__main__":
    main()

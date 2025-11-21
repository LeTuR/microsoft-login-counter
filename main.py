"""Main entry point for Microsoft Login Counter proxy."""
import sys
import logging
from pathlib import Path

from mitmproxy.tools.main import mitmdump

from src.config.loader import ConfigLoader
from src.logging.setup import setup_logging
from src.storage.database import Database
from src.proxy.addon import LoginDetectorAddon

logger = logging.getLogger(__name__)


def main():
    """Start the Microsoft Login Counter proxy."""
    # Load configuration
    config_loader = ConfigLoader('config.yaml')
    config = config_loader.load()

    # Setup logging
    setup_logging(config)

    logger.info("=" * 60)
    logger.info("Microsoft Login Counter - Starting")
    logger.info("=" * 60)

    # Initialize database
    db_path = config['storage']['database_path']
    logger.info(f"Initializing database: {db_path}")

    db = Database(db_path)
    db.connect()
    db.initialize_schema()
    db.close()

    logger.info("Database initialized successfully")

    # Create addon
    callback_timeout = config['detection']['callback_timeout']
    addon = LoginDetectorAddon(
        database_path=db_path,
        callback_timeout=callback_timeout
    )

    # Configure mitmproxy arguments
    proxy_port = config['proxy']['port']
    listen_address = config['proxy']['listen_address']
    upstream_proxy = config['proxy'].get('upstream_proxy')

    mitmdump_args = [
        '--listen-host', listen_address,
        '--listen-port', str(proxy_port),
        '--set', 'block_global=false',
    ]

    if upstream_proxy:
        mitmdump_args.extend(['--mode', f'upstream:{upstream_proxy}'])

    logger.info(f"Starting mitmproxy on {listen_address}:{proxy_port}")
    if upstream_proxy:
        logger.info(f"Using upstream proxy: {upstream_proxy}")

    logger.info("=" * 60)
    logger.info("Proxy is ready to detect Microsoft logins")
    logger.info(f"Configure your browser to use proxy: {listen_address}:{proxy_port}")
    logger.info("=" * 60)

    # Start mitmproxy with addon
    import asyncio
    from mitmproxy import options
    from mitmproxy.tools import dump

    async def start_proxy():
        """Start the proxy with our addon."""
        opts = options.Options(
            listen_host=listen_address,
            listen_port=proxy_port,
        )

        master = dump.DumpMaster(opts)
        master.addons.add(addon)

        try:
            await master.run()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            master.shutdown()

    try:
        asyncio.run(start_proxy())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)


# Mitmproxy entry point for addon
def start():
    """Return addon instance for mitmproxy."""
    config_loader = ConfigLoader('config.yaml')
    config = config_loader.load()

    db_path = config['storage']['database_path']
    callback_timeout = config['detection']['callback_timeout']

    return LoginDetectorAddon(
        database_path=db_path,
        callback_timeout=callback_timeout
    )


# For direct mitmproxy script execution
addons = [start()]


if __name__ == '__main__':
    main()

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from smart_contracts._helpers.build import build
from smart_contracts._helpers.config import contracts

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)-10s: %(message)s"
)
logger = logging.getLogger(__name__)
logger.info("Loading .env")
# For manual script execution (bypassing `algokit project deploy`) with a custom .env,
# modify `load_dotenv()` accordingly. For example, `load_dotenv('.env.localnet')`.
load_dotenv()
root_path = Path(__file__).parent


def main(action: str, contract_name: str | None = None) -> None:
    artifact_path = root_path / "artifacts"

    # Filter contracts if a specific contract name is provided
    filtered_contracts = [
        c for c in contracts if contract_name is None or c.name == contract_name
    ]

    match action:
        case "build":
            for contract in filtered_contracts:
                logger.info(f"Building app at {contract.path}")
                build(artifact_path / contract.name, contract.path)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main("build")

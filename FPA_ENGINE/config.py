from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FPAConfig:
    """
    Configuration for the FP&A input and forecasting layer.

    This configuration contains paths and structural settings,
    not financial values.
    """

    dataset_dir: Path
    data_version: str = "True_data"

    @property
    def data_version_dir(self) -> Path:
        return self.dataset_dir / self.data_version

    @property
    def current_data_dir(self) -> Path:
        return self.data_version_dir / "current_data"

    @property
    def prior_data_dir(self) -> Path:
        return self.data_version_dir / "prior_data"

    @property
    def output_dir(self) -> Path:
        return Path("OUTPUT")
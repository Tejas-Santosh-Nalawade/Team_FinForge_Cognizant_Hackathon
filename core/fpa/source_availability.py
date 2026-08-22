from pathlib import Path

import pandas as pd

from core.fpa.source_catalog import build_source_catalog
from core.fpa.planning_source_discovery import PlanningSourceDiscovery


class SourceAvailabilityValidator:
    """
    Determines which registered FP&A and qualitative sources
    are available in the dataset.

    This class does not generate financial values.

    It only reports source availability based on discovered
    files and registered source categories.
    """

    def __init__(
        self,
        dataset_dir: str | Path,
        data_version: str = "True_data",
    ):
        self.dataset_dir = Path(dataset_dir)
        self.data_version = data_version

        self.source_registry = build_source_catalog()

        self.discovery = PlanningSourceDiscovery(
            dataset_dir=self.dataset_dir,
            data_version=self.data_version,
        )

    def _planning_source_categories(self) -> set[str]:
        """
        Return planning categories registered in the
        central source registry.
        """

        planning_categories = {
            "AOB",
            "4Q_rolling_forecast",
            "8Q_rolling_forecast",
            "operational_drivers",
        }

        registered_categories = set(
            self.source_registry
            .to_dataframe()["source_category"]
        )

        return planning_categories.intersection(
            registered_categories
        )

    def validate_planning_sources(self) -> pd.DataFrame:
        """
        Validate availability of forward-looking planning sources.

        A source is AVAILABLE only when the discovery engine
        finds supporting workbook evidence.

        Otherwise it is reported as MISSING.
        """

        discovered = (
            self.discovery
            .discover_planning_sources()
        )

        records = []

        for category in sorted(
            self._planning_source_categories()
        ):

            matches = discovered[
                discovered["category"] == category
            ]

            if matches.empty:

                records.append(
                    {
                        "source_category": category,
                        "status": "MISSING",
                        "files_found": "",
                        "evidence": "",
                    }
                )

            else:

                records.append(
                    {
                        "source_category": category,
                        "status": "AVAILABLE",
                        "files_found": "; ".join(
                            sorted(
                                matches["file"]
                                .unique()
                            )
                        ),
                        "evidence": "; ".join(
                            sorted(
                                matches[
                                    "matched_evidence"
                                ]
                                .dropna()
                                .unique()
                            )
                        ),
                    }
                )

        return pd.DataFrame(records)

    def validate_all_registered_sources(self) -> pd.DataFrame:
        """
        Return the registry-level source inventory.

        Planning sources are checked through content discovery.

        Other sources are currently marked as NOT_EVALUATED
        because they require their own ingestion/discovery logic.

        No source values are generated.
        """

        planning_status = (
            self.validate_planning_sources()
        )

        planning_lookup = {
            row["source_category"]: row
            for _, row in planning_status.iterrows()
        }

        records = []

        registry_df = (
            self.source_registry
            .to_dataframe()
        )

        for _, source in registry_df.iterrows():

            category = source["source_category"]

            if category in planning_lookup:

                result = planning_lookup[
                    category
                ]

                records.append(
                    {
                        "source_id": source["source_id"],
                        "source_category": category,
                        "authority_level": source[
                            "authority_level"
                        ],
                        "required": source["required"],
                        "status": result["status"],
                        "files_found": result[
                            "files_found"
                        ],
                        "evidence": result[
                            "evidence"
                        ],
                    }
                )

            else:

                records.append(
                    {
                        "source_id": source["source_id"],
                        "source_category": category,
                        "authority_level": source[
                            "authority_level"
                        ],
                        "required": source["required"],
                        "status": "NOT_EVALUATED",
                        "files_found": "",
                        "evidence": "",
                    }
                )

        return pd.DataFrame(records)
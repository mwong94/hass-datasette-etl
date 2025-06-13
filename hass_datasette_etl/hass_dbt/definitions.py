from pathlib import Path

from dagster_dbt import DbtCliResource, DbtProject, dbt_assets, build_schedule_from_dbt_selection, DagsterDbtTranslator
import dagster as dg
from typing import Mapping, Any, Optional

# Points to the dbt project path
dbt_project_directory = Path(__file__).absolute().parent
dbt_project = DbtProject(
    project_dir=dbt_project_directory,
    profiles_dir=dbt_project_directory.parent / "profiles",
)

# References the dbt project object
dbt_resource = DbtCliResource(project_dir=dbt_project)

# Compiles the dbt project & allow Dagster to build an asset graph
dbt_project.prepare_if_dev()


class CustomDagsterDbtTranslator(DagsterDbtTranslator):
    def get_asset_key(self, dbt_resource_props: Mapping[str, Any]) -> dg.AssetKey:
        return super().get_asset_key(dbt_resource_props).with_prefix("dbt")
    def get_group_name(self, dbt_resource_props: Mapping[str, Any]) -> Optional[str]:
        return "dbt"


# Yields Dagster events streamed from the dbt CLI
@dbt_assets(manifest=dbt_project.manifest_path, dagster_dbt_translator=CustomDagsterDbtTranslator())
def dbt_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()


# Builds a daily refresh schedule
dbt_schedule = build_schedule_from_dbt_selection(
    [dbt_models],
    job_name="materialize_dbt_models",
    cron_schedule="30 0 * * *",
    execution_timezone="America/Los_Angeles",
    dbt_select="fqn:*"
)


# Dagster object that contains the dbt assets and resource
dbt_defs = dg.Definitions(
    assets=[dbt_models],
    resources={"dbt": dbt_resource},
    schedules=[dbt_schedule]
)

from pathlib import Path

import tomllib
import yaml

root_dir = Path(__file__).parent.parent

pyproject_path = root_dir / "pyproject.toml"
pre_commit_config_path = root_dir / ".pre-commit-config.yaml"

with open(pyproject_path, "rb") as fp:
    pyproject = tomllib.load(fp)

project_data = pyproject.get("project", {})
main_deps = project_data.get("dependencies", [])

optional_deps_map = project_data.get("optional-dependencies", {})
optional_deps = [item for sublist in optional_deps_map.values() for item in sublist]

dev_deps = pyproject.get("dependency-groups", {}).get("dev", [])

all_deps = sorted(list(set(main_deps + optional_deps + dev_deps)))

with open(pre_commit_config_path, "r") as fp:
    pre_commit_config = yaml.safe_load(fp)

for repo in pre_commit_config.get("repos", []):
    for hook in repo.get("hooks", []):
        hook["additional_dependencies"] = all_deps

with open(pre_commit_config_path, "w") as fw:
    noalias_dumper = yaml.dumper.Dumper
    noalias_dumper.ignore_aliases = lambda self, data: True
    yaml.dump(
        pre_commit_config,
        fw,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        Dumper=noalias_dumper,
    )

print("Synced pre-commit dependencies successfully.")

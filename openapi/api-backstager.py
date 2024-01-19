#!/usr/bin/env python3
# python3 -m pip install -U python-gitlab pyyaml
# Run:
# python api-backstager.py

import gitlab
import os
import sys
import yaml
import pathlib
import re


def list_documents(gl: gitlab.Gitlab, group_id):
    group = gl.groups.get(group_id)
    project_ids = []
    for project in group.projects.list(include_subgroups=True, all=True):
        if project.name == "Documents":
            print(f"{project.id}:{project.name}")
            project_ids.append(project.id)
    return project_ids


def catalog_apis(gl: gitlab.Gitlab, project_id: int):
    project = gl.projects.get(project_id)
    system = project.name_with_namespace.split("/")[1].strip()
    apis = []
    for file in project.repository_tree(
        path="", ref="master", recursive=True, get_all=True
    ):
        filename = file["name"]
        if pathlib.Path(filename).suffix == ".yaml":
            try:
                raw_file_path = f'{project.web_url}/blob/master/{file["path"]}'
                raw_file_content = project.files.get(
                    file_path=file["path"], ref="master"
                )
                api_info = bs_make_api_info(
                    raw_file_content.decode(), system, raw_file_path
                )
                apis.append(api_info)
            except Exception as error:
                print(f"{filename} has errors:", error)
    print(f"System {system} found apis: {len(apis)}")
    if apis:
        with open(f"{system}-api-info.yaml", "w") as stream:
            yaml.dump_all(apis, stream, default_flow_style=False)


def api_info(api_name, api_version, api_description, system, api_url):
    normalized_api_name = re.sub(r"[\W_]+", "_", api_name)
    return {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "API",
        "metadata": {
            "name": f"{normalized_api_name}-{api_version}",
            "description": api_description,
            "annotations": {"backstage.io/source-location": "url:" + api_url},
        },
        "spec": {
            "type": "openapi",
            "lifecycle": "production",
            "owner": "api-team",
            "system": system,
            "definition": {"$text": api_url},
        },
    }


def bs_make_api_info(api_spec_content: bytes, system: str, url: str):
    api_spec = yaml.safe_load(api_spec_content)
    info = api_spec["info"]
    return api_info(info["title"], info["version"], info["description"], system, url)


def main():
    REPO_SERVER = os.environ.get("REPO_SERVER", "https://gitlab.com")
    REPO_TOKEN = os.environ.get("REPO_TOKEN")

    if not REPO_TOKEN:
        print("Please set the REPO_TOKEN env variable, this would be repo read access Personal Access Token")
        sys.exit(1)

    gl = gitlab.Gitlab(url=REPO_SERVER, private_token=REPO_TOKEN)
    # gl.enable_debug()

    # Project Ids where Open API specs reside
    spec_project_ids = [450]
    for project_id in spec_project_ids:
        catalog_apis(gl, project_id)


if __name__ == "__main__":
    exit(main())

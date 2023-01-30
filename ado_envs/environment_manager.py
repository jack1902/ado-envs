import json
import logging
from argparse import Namespace

from ado_envs.devops import DevOps

LOGGER = logging.getLogger(__name__)


def create(client: DevOps, args: Namespace):
    """create environments or resources in Azure DevOps
    Args:
        client (DevOps): Instantiated DevOps class
        args (Namespace): CLI Args

    Returns:
        bool: The return value. True for success, False otherwise.
    """
    env_name = args.environment
    resources = args.resources

    env = None
    if env := client.get_environment(env_name):
        print(f"Environment {env_name} already exists")
    elif env := client.create_environment(env_name):
        print(f"Created environment {env_name}")
    else:
        print(f"Failed to create environment {env_name}")
        return

    # No resources to create were specified, exit early
    if not resources:
        return True

    service_endpoint = client.get_service_endpoint(env_name, "kubernetes")
    if not service_endpoint:
        LOGGER.error(
            f"Failed to locate a service-connection with name: {env_name}. Please create it via the UI"
        )
        return

    existing_resources = [
        resource["name"] for resource in client.get_environment_resources(str(env["id"]), env_name)
    ]

    for resource in resources:
        if resource in existing_resources:
            print(f"Resource '{resource}' already exists")
            continue

        response = client.create_environment_resource(
            env["id"],
            {
                "clusterName": env_name,
                "name": resource,
                "namespace": resource,
                "serviceEndpointId": service_endpoint["id"],
            },
        )
        if response:
            print(f"Resource '{resource}' created")
        else:
            print(f"Failed to create resource '{resource}'")
            return

    return True


def _list(client, args):
    if args.environments:
        environments = client.get_environments()
        if not environments:
            print("Failed to fetch environments")
            return

        environments = [
            {"id": env["id"], "name": env["name"], "description": env["description"]}
            for env in environments
        ]

        print(json.dumps(environments))

    if args.resources:
        env = client.get_environment(args.resources)
        resources = client.get_environment_resources(str(env["id"]), env["name"])
        print(json.dumps(resources))


def update(client, args):
    """update environments or resources in Azure DevOps
    Args:
        client (DevOps): Instantiated DevOps class
        args (Namespace): CLI Args

    Returns:
        bool: The return value. True for success, False otherwise.
    """

    raise NotImplementedError


def delete(client, args):
    env_name = args.environment
    resources = args.resources

    if env_name:
        env = next(env for env in client.get_environments() if env["name"] == env_name)
        if not env:
            print(f"Failed to find the given environment: {env_name}")
            return

        if not client.delete_environment(env_name, env["id"]):
            print(f"Failed to delete environment {env_name}")
            return

        print(f"Deleted environment {env_name}")
        return True

    if resources:
        for env in client.get_environments():
            for resource in client.get_environment_resources(str(env["id"]), env["name"]):
                if resource["name"] in resources:
                    print(f"Deleting resource {resource['name']} within {env['name']}")
                    client.delete_resource(env, resources)

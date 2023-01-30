import argparse
import os

from ado_envs.devops import DevOps
from ado_envs.environment_manager import _list, create, delete, update


def main():
    global_parser = argparse.ArgumentParser(
        description="Manage Azure DevOps Pipeline Environments and Kubernetes Resources",
        prog="ado-envs",
    )

    global_parser.add_argument(
        "--pat",
        dest="personal_access_token",
        default=os.getenv("PAT_TOKEN"),
        help="Your Personal Access Token for the Azure DevOps API (defaults to PAT_TOKEN environment-variable)",
    )

    global_parser.add_argument(
        "--organization",
        "-o",
        required=True,
        help="The organization to target within Azure DevOps",
    )
    global_parser.add_argument(
        "--project",
        "-p",
        required=True,
        help="The project to target in the given organization",
    )

    subparsers = global_parser.add_subparsers(
        help="The action to take against azure-devops", required=True
    )

    # Create sub-command Parser
    create_subparser = subparsers.add_parser("create", help="Create an environment or resource")
    create_subparser.add_argument("environment", type=str)
    create_subparser.add_argument(
        "--resources",
        action="extend",
        nargs="+",
        help="Resource name",
    )
    create_subparser.set_defaults(func=create)

    # list sub-command Parser
    list_subparser = subparsers.add_parser("list", help="list environments or resources")
    list_subparser.set_defaults(func=_list)
    list_mutual_group = list_subparser.add_mutually_exclusive_group(required=True)
    list_mutual_group.add_argument(
        "--resources",
        nargs="?",
        help="List all visible resources within the given environment",
        metavar="env",
    )
    list_mutual_group.add_argument(
        "--environments",
        default=False,
        action="store_true",
        help="List all visible resources within the given environment",
    )

    # Update sub-command Parser
    update_subparser = subparsers.add_parser("update", help="Update an environment or resource")
    update_subparser.add_argument("environment", type=str)
    update_subparser.add_argument(
        "--resources",
        action="extend",
        nargs="+",
        help="Resource name",
    )
    update_subparser.set_defaults(func=update)

    # Delete sub-command Parser
    delete_subparser = subparsers.add_parser("delete", help="Delete an environment or resource")
    delete_mutual_group = delete_subparser.add_mutually_exclusive_group(required=True)
    delete_mutual_group.add_argument(
        "--resources",
        action="extend",
        nargs="+",
        help="Delete all given resources across all environments",
    )
    delete_mutual_group.add_argument(
        "--environment",
        type=str,
        help="Delete the given environment",
    )
    delete_subparser.set_defaults(func=delete)

    args = global_parser.parse_args()
    if not args.personal_access_token:
        global_parser.error("Please set your Personal Access Token via --pat OR env-var: PAT_TOKEN")

    client = DevOps(args.organization, args.project, args.personal_access_token)

    success = args.func(client, args)
    global_parser.exit(0 if success else 1)

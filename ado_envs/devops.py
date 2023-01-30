import logging

import requests

LOGGER = logging.getLogger(__name__)


class DevOps:
    def __init__(self, organization: str, project: str, pat_token: str):
        self.base_url = f"https://dev.azure.com/{organization}/{project}"
        self.organization = organization
        self.project = project
        self.session = requests.Session()
        self.session.auth = ("", pat_token)

    def make_request(self, method: str, uri: str, raise_error=True, **kwargs):
        url = f"{self.base_url}/_apis/{uri}"
        LOGGER.debug(url)

        try:
            response = self.session.request(method, url, **kwargs)
            if raise_error:
                response.raise_for_status()
        except Exception as e:
            LOGGER.error(e)
        else:
            return response

    def get_environments(self):
        LOGGER.debug("Getting existing environments")

        response = self.make_request(
            "get", "distributedtask/environments", params={"api-version": "7.0"}
        )

        return response.json()["value"] if response else None

    def get_environment(self, env_name: str):
        LOGGER.debug(f"Getting environment {env_name}")

        environments = self.get_environments()
        if not environments:
            return

        for environment in environments:
            if environment["name"] == env_name:
                return environment

    def create_environment(self, env_name: str):
        LOGGER.debug(f"Creating environment {env_name}")

        response = self.make_request(
            "post",
            "distributedtask/environments",
            params={"api-version": "7.0"},
            json={"description": "", "name": env_name},
        )

        return response.json() if response else None

    def delete_environment(self, environment_name: str, environment_id: str):
        LOGGER.debug(f"Deleting environment {environment_name}")

        response = self.make_request(
            "delete",
            f"distributedtask/environments/{environment_id}",
            params={"api-version": "7.0"},
        )

        return response if response else None

    def get_service_endpoints(self):
        LOGGER.debug("Getting service endpoints")

        response = self.make_request(
            "get", "serviceendpoint/endpoints", params={"api-version": "6.0-preview.4"}
        )

        return response.json()["value"] if response else None

    def get_service_endpoint(self, endpoint_name: str, endpoint_type: str):
        LOGGER.debug(f"Getting service endpoint {endpoint_name} with type {endpoint_type}")

        service_endpoints = self.get_service_endpoints()
        if not service_endpoints:
            return

        for service_endpoint in service_endpoints:
            if (
                service_endpoint["type"] == endpoint_type
                and service_endpoint["name"] == endpoint_name
            ):
                return service_endpoint

    def delete_service_endpoint(self, endpoint_id, project_id):
        LOGGER.debug(f"Deleting service endpoint {endpoint_id}")
        response = self.make_request(
            "delete",
            f"serviceendpoint/endpoints/{endpoint_id}",
            params={"projectIds": project_id, "api-version": "6.0-preview.4"},
        )

        return response

    def get_environment_resources(self, environment_id: str, environment_name: str):
        LOGGER.debug(f"Getting environment resources for environment {environment_name}")

        response = self.make_request(
            "get",
            "distributedtask/environments/" + environment_id,
            params={"expands": "resourceReferences", "api-version": "6.0-preview.1"},
        )

        return response.json()["resources"] if response else None

    def create_environment_resource(self, environment_id: str, resource: dict):
        LOGGER.debug(f"Creating resource {resource['name']}")
        response = self.make_request(
            "post",
            f"distributedtask/environments/{environment_id}/providers/kubernetes?api-version=6.0-preview.1",
            params={},
            json=resource,
        )
        return response

    def delete_environment_resource(self, environment_id: str, resource: str):
        LOGGER.debug(f"Deleting resource {resource}")

        return self.make_request(
            "delete",
            f"distributedtask/environments/{environment_id}/providers/kubernetes?api-version=6.0-preview.1",
            params={},
            json=resource,
        )

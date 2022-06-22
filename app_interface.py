import sys

from ruamel.yaml import YAML

from git_helpers import init_repo, get_sha_date
from pprint import pprint


NAMESPACE_PREFIX = "/services/insights/ccx-data-pipeline/namespaces/"
yaml = YAML()
yaml.preserve_quotes = True  # app-interface uses double quotes
yaml.explicit_start = True  # in order not to remove the "---"


def read_yaml(yaml_file):
    """Read a YAML file and returns the parsed object."""
    with open(yaml_file) as f:
        y = yaml.load(f)
        return y


def get_resourceNamespace(y, service, namespace):
    """Get the resource by service and namespace.

    Note that the namespace given as parameter shouldn't contain the NAMESPACE_PREFIX.
    """
    for resource in y["resourceTemplates"]:
        if resource["name"] == service:
            for resourceNamespace in resource["targets"]:
                if (
                    NAMESPACE_PREFIX + namespace
                    in resourceNamespace["namespace"]["$ref"]
                ):
                    return resourceNamespace
            raise KeyError(
                f"Couldn't find the namespace {NAMESPACE_PREFIX + namespace} in {y}"
            )
    raise KeyError(f"Couldn't find the service {service} in {y}")


def get_services(y):
    services = []
    for resource in y["resourceTemplates"]:
        services.append(resource["name"])
    return services


def get_namespaces(y, service):
    namespaces = []
    for resource in y["resourceTemplates"]:
        if resource["name"] == service:
            for resourceNamespace in resource["targets"]:
                ns = resourceNamespace["namespace"]["$ref"]
                if ns.startswith(NAMESPACE_PREFIX):
                    ns = ns[len(NAMESPACE_PREFIX) :]
                    namespaces.append(ns)
            return namespaces
    raise KeyError(f"Couldn't find the service {service} in {y}")


def check_sha_is_newer(y, service, new_sha, namespace):
    """Check the $service SHA located in the namespace ref is older than the new one."""
    # Using `/tmp/service` as the default path for the service git repository
    old_sha = get_resourceNamespace(y, service, namespace)["ref"]

    repo = init_repo(f"/tmp/{service}")
    old_sha_date = get_sha_date(repo, old_sha)
    new_sha_date = get_sha_date(repo, new_sha)

    assert new_sha_date > old_sha_date


def update_sha(y, service, new_sha, namespace):
    """Update the $service SHA located in the namespace ref."""
    old_resource = get_resourceNamespace(y, service, namespace)
    old_resource["ref"] = new_sha


def replace_sha(y, service, new_sha, namespace, file_path):
    """Replace the $service SHA located in the namespace ref writing to the file."""
    update_sha(y, service, new_sha, namespace)

    with open(file_path, "w") as f:
        yaml.dump(y, f)


def get_sha(y, service, namespace):
    """Get the SHA of a given service and namespace."""
    return get_resourceNamespace(y, service, namespace)["ref"]


def check_sha_is(y, service, want_sha, namespace):
    """Check the $service SHA located in the namespace ref is the same as $want_sha."""
    got_sha = get_sha(y, service, namespace)
    assert want_sha == got_sha, f"got SHA {got_sha} but want {want_sha}"


if __name__ == "__main__":
    FILE_PATH = "test_deploy.yml"
    SERVICE = "ccx-data-pipeline"
    NAMESPACE = "ccx-data-pipeline-prod.yml"

    print("Reading:\n", FILE_PATH)
    y = read_yaml(FILE_PATH)

    services = get_services(y)
    print("Available services are (limited to 5 for readability):")
    pprint(services[:5])

    namespaces = get_namespaces(y, SERVICE)
    print(f"Available namespaces for {SERVICE} are:")
    pprint(namespaces)

    print(f"The SHA of {SERVICE} in {NAMESPACE} is:")
    sha = get_sha(y, SERVICE, NAMESPACE)
    pprint(sha)

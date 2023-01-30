# ado-envs

Create an environment within Azure DevOps Pipelines, along with the resources given. This is extremely useful as it ensures one service-connection can be used for multiple resources which is NOT possible via the UI.

## Pre-reqs

Ensure you have the version of python specified within `.python-version`, along with the requirements installed from `requirements.txt` and a Personal Access Token for Azure DevOps exported as an env-var `PAT_TOKEN` or passed via the command line using `--pat`

```sh
python -m venv venv
source venv/bin/active
pip install .
```

## Create

```sh
# Create an env named `example` with resources a,b,c
ado-envs -o "${PROJECT}" -p "${PROJECT}" create example --resources a b c
```

## List

```sh
# List environments
ado-envs -o "${PROJECT}" -p "${PROJECT}" list --environments

# List resources
ado-envs -o "${PROJECT}" -p "${PROJECT}" list --resources "${ENV_NAME}"
```

## Delete

```sh
# Delete a whole environment
ado-envs -o "${PROJECT}" -p "${PROJECT}" delete "${ENV_NAME}"

# Delete specified resources ONLY from the given env-name
ado-envs -o "${PROJECT}" -p "${PROJECT}" delete "${ENV_NAME}" --resource a b c
```

from os.path import expanduser

home = expanduser("~")

# This is the path where you store the repositories f.e:
# /home/jdiazsua/Documents/Projects
# ├── app-interface
# ├── ccx-data-pipeline
# ├── ccx-notification-service
# ├── ccx-notification-writer
# ├── insights-content-service
# ├── insights-operator-gathering-conditions-service
# ├── insights-results-aggregator
# ├── insights-results-aggregator-exporter
# ├── insights-results-smart-proxy
REPOSITORIES_FOLDER = f"{home}/Documents/Projects"

# This is the path where the deploy.yml is located
PATH_TO_DEPLOY_YML = f"{REPOSITORIES_FOLDER}/app-interface/data/services/insights/ccx-data-pipeline/deploy.yml"

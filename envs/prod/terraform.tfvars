project_id = "enterprise-ci-cd-ai" # consider a dedicated production project

# REQUIRED: planning fails until at least one CIDR is listed. Example:
#   authorized_networks = [{ cidr = "203.0.113.0/24", name = "office-vpn" }]
authorized_networks = []

# Repository whose GitHub Actions may deploy to this environment (owner/repo). Leave empty to skip.
# The job must run in a GitHub environment named "prod".
github_repository = ""

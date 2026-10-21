project_id = "enterprise-ci-cd-ai"

# Optional for dev. Example: [{ cidr = "203.0.113.0/24", name = "office" }]
authorized_networks = []

# Repository whose GitHub Actions may deploy to this environment (owner/repo). Leave empty to skip.
# The job must run in a GitHub environment named "dev".
github_repository = ""

# Lets ONE GitHub repository, running ONE GitHub environment (dev, stage or prod), deploy to this
# environment's cluster. There are no long-lived keys: GitHub proves who it is with a short-lived OIDC token
# (Workload Identity Federation) and receives temporary credentials for a dedicated deployer service account.
#
# Isolation: this environment has its own pool, provider and service account, and the provider only accepts tokens
# whose repository AND GitHub environment match. A dev pipeline therefore cannot impersonate the prod deployer.

locals {
  roles = concat(
    ["roles/container.developer"], # deploy workloads into the cluster
    var.enable_connect_gateway ? [
      "roles/gkehub.gatewayEditor", # reach the cluster through the Connect gateway (works with private/locked-down APIs)
      "roles/gkehub.viewer",
    ] : [],
  )
}

# Pool IDs stay reserved for 30 days after a delete, so a random suffix lets you destroy and rebuild immediately.
resource "random_id" "pool" {
  byte_length = 3
}

resource "google_service_account" "deployer" {
  project      = var.project_id
  account_id   = "${var.name}-gha"
  display_name = "GitHub Actions deployer for ${var.name}"
}

resource "google_project_iam_member" "deployer" {
  for_each = toset(local.roles)

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.deployer.email}"
}

# Push images to this environment's registry only.
resource "google_artifact_registry_repository_iam_member" "push" {
  project    = var.project_id
  location   = var.registry_location
  repository = var.registry_id
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.deployer.email}"
}

resource "google_iam_workload_identity_pool" "github" {
  project                   = var.project_id
  workload_identity_pool_id = "${var.name}-gh-${random_id.pool.hex}"
  display_name              = "GitHub Actions (${var.name})"
}

resource "google_iam_workload_identity_pool_provider" "github" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github"
  display_name                       = "GitHub OIDC"

  attribute_mapping = {
    "google.subject"        = "assertion.sub"
    "attribute.repository"  = "assertion.repository"
    "attribute.environment" = "assertion.environment"
  }

  # Reject every token that is not from this repository running in this GitHub environment.
  attribute_condition = "assertion.repository == \"${var.github_repository}\" && assertion.environment == \"${var.github_environment}\""

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account_iam_member" "impersonate" {
  service_account_id = google_service_account.deployer.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_repository}"
}

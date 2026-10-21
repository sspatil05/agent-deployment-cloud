# Docker repository that holds the agent images for one environment.
resource "google_artifact_registry_repository" "this" {
  project       = var.project_id
  location      = var.region
  repository_id = var.name
  format        = "DOCKER"
  description   = "Agent container images (${var.name})"
  labels        = var.labels

  docker_config {
    immutable_tags = var.immutable_tags
  }

  # Keep storage (and cost) in check: drop untagged layers after a while, always keep recent versions.
  cleanup_policy_dry_run = false

  cleanup_policies {
    id     = "delete-old-untagged"
    action = "DELETE"
    condition {
      tag_state  = "UNTAGGED"
      older_than = "${var.untagged_retention_days * 86400}s"
    }
  }

  cleanup_policies {
    id     = "keep-recent-versions"
    action = "KEEP"
    most_recent_versions {
      keep_count = var.keep_recent_versions
    }
  }
}

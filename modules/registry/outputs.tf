output "repository_id" {
  value = google_artifact_registry_repository.this.repository_id
}

output "image_path" {
  description = "Prefix for image names: <image_path>/<agent>:<tag>"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.this.repository_id}"
}

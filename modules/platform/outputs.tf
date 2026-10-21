output "cluster_name" {
  value = module.gke.cluster_name
}

output "get_credentials_command" {
  value = "gcloud container clusters get-credentials ${module.gke.cluster_name} --location ${var.location} --project ${var.project_id}"
}

output "vpc_name" {
  value = module.vpc.network_name
}

output "image_path" {
  description = "Push agent images to <image_path>/<agent>:<tag>"
  value       = module.registry.image_path
}

output "docker_auth_command" {
  value = "gcloud auth configure-docker ${var.region}-docker.pkg.dev"
}

output "worker_node_count" {
  description = "Total worker nodes (workers per zone x zones that hold nodes)."
  value       = var.workers_per_zone * (var.node_locations == null ? 1 : length(var.node_locations))
}

output "node_service_account" {
  value = module.gke.node_service_account
}

output "github_wif_provider" {
  description = "GitHub environment secret GCP_WIF_PROVIDER (null until github_repository is set)."
  value       = one(module.github_actions[*].workload_identity_provider)
}

output "github_service_account" {
  description = "GitHub environment secret GCP_SERVICE_ACCOUNT (null until github_repository is set)."
  value       = one(module.github_actions[*].service_account_email)
}

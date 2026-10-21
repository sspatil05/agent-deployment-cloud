output "cluster_name" {
  value = module.platform.cluster_name
}

output "get_credentials_command" {
  value = module.platform.get_credentials_command
}

output "vpc_name" {
  value = module.platform.vpc_name
}

output "worker_node_count" {
  value = module.platform.worker_node_count
}

output "image_path" {
  value = module.platform.image_path
}

output "docker_auth_command" {
  value = module.platform.docker_auth_command
}
output "github_wif_provider" {
  description = "Set as GitHub environment secret GCP_WIF_PROVIDER"
  value       = module.platform.github_wif_provider
}

output "github_service_account" {
  description = "Set as GitHub environment secret GCP_SERVICE_ACCOUNT"
  value       = module.platform.github_service_account
}

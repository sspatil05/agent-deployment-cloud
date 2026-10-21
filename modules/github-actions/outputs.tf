output "workload_identity_provider" {
  description = "Value for the GitHub environment secret GCP_WIF_PROVIDER."
  value       = google_iam_workload_identity_pool_provider.github.name
}

output "service_account_email" {
  description = "Value for the GitHub environment secret GCP_SERVICE_ACCOUNT."
  value       = google_service_account.deployer.email
}

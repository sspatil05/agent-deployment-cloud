variable "project_id" {
  type = string
}

variable "name" {
  type        = string
  description = "Environment name prefix, e.g. agents-dev."
}

variable "github_repository" {
  type        = string
  description = "owner/repo whose workflows may deploy, e.g. my-org/my-agents."

  validation {
    condition     = can(regex("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", var.github_repository))
    error_message = "github_repository must look like owner/repo."
  }
}

variable "github_environment" {
  type        = string
  description = "GitHub environment (Settings > Environments) the workflow job must run in, e.g. dev."
}

variable "registry_location" {
  type = string
}

variable "registry_id" {
  type        = string
  description = "Artifact Registry repository the deployer may push to."
}

variable "enable_connect_gateway" {
  type        = bool
  default     = true
  description = "Grant the Connect gateway roles so kubectl works even when the API server is locked to private CIDRs."
}

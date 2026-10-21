variable "project_id" {
  type        = string
  description = "Google Cloud project that hosts this environment."
}

variable "region" {
  type        = string
  default     = "asia-south1" # Mumbai
  description = "Region for the VPC, registry and cluster."
}

variable "authorized_networks" {
  type = list(object({
    cidr = string
    name = string
  }))
  default     = []
  description = "CIDRs allowed to reach the Kubernetes API, e.g. [{ cidr = \"203.0.113.0/24\", name = \"office\" }]."
}
variable "github_repository" {
  type        = string
  default     = ""
  description = "owner/repo that may deploy to this environment, e.g. my-org/my-apps. Empty = no pipeline identity."
}

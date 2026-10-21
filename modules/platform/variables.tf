variable "project_id" {
  type = string
}

variable "environment" {
  type        = string
  description = "dev, stage or prod. Becomes part of every resource name."
}

variable "region" {
  type = string
}

variable "location" {
  type        = string
  description = "Cluster location: a zone (zonal, one control plane) or the region (regional, HA control plane)."
}

variable "node_locations" {
  type        = list(string)
  default     = null
  description = "Zones that hold workers. Required when location is a region."
}

variable "subnet_cidr" {
  type = string
}

variable "pods_cidr" {
  type = string
}

variable "services_cidr" {
  type = string
}

variable "master_cidr" {
  type    = string
  default = "172.17.0.0/28"
}

variable "enable_private_nodes" {
  type    = bool
  default = false
}

variable "authorized_networks" {
  type = list(object({
    cidr = string
    name = string
  }))
  default = []
}

variable "require_authorized_networks" {
  type    = bool
  default = false
}

variable "deletion_protection" {
  type    = bool
  default = true
}

variable "release_channel" {
  type    = string
  default = "REGULAR"
}

variable "workers_per_zone" {
  type    = number
  default = 2
}

variable "machine_type" {
  type    = string
  default = "e2-medium"
}

variable "disk_size_gb" {
  type    = number
  default = 50
}

variable "disk_type" {
  type    = string
  default = "pd-balanced"
}

variable "immutable_image_tags" {
  type    = bool
  default = false
}

variable "labels" {
  type    = map(string)
  default = {}
}

variable "github_repository" {
  type        = string
  default     = ""
  description = "owner/repo allowed to deploy to this environment via GitHub Actions. Empty = no CI/CD identity is created."
}

variable "enable_connect_gateway" {
  type        = bool
  default     = true
  description = "Register the cluster with the fleet and allow deploys through the Connect gateway."
}

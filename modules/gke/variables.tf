variable "project_id" {
  type = string
}

variable "name" {
  type        = string
  description = "Cluster name, e.g. agents-dev-cluster."
}

variable "location" {
  type        = string
  description = "A zone (zonal cluster, one control plane) or a region (regional cluster, HA control plane)."
}

variable "node_locations" {
  type        = list(string)
  default     = null
  description = "Zones that hold worker nodes. Needed for regional clusters; leave null for zonal."
}

variable "network_id" {
  type = string
}

variable "subnet_id" {
  type = string
}

variable "pods_range_name" {
  type = string
}

variable "services_range_name" {
  type = string
}

variable "release_channel" {
  type    = string
  default = "REGULAR"
}

variable "enable_private_nodes" {
  type        = bool
  default     = false
  description = "Worker nodes without public IPs. The VPC then needs Cloud NAT for outbound traffic."
}

variable "master_cidr" {
  type        = string
  default     = "172.17.0.0/28"
  description = "/28 for the private control plane endpoint; used only when enable_private_nodes is true."
}

variable "authorized_networks" {
  type = list(object({
    cidr = string
    name = string
  }))
  default     = []
  description = "CIDRs allowed to reach the Kubernetes API. Empty = no restriction."
}

variable "require_authorized_networks" {
  type        = bool
  default     = false
  description = "Refuse to plan unless authorized_networks is set."
}

variable "enable_fleet" {
  type        = bool
  default     = false
  description = "Register the cluster with the project fleet (enables the Connect gateway)."
}

variable "deletion_protection" {
  type    = bool
  default = true
}

variable "workers_per_zone" {
  type        = number
  default     = 2
  description = "Worker nodes in each zone that holds nodes."
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

variable "labels" {
  type    = map(string)
  default = {}
}

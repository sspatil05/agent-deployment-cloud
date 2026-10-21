variable "project_id" {
  type        = string
  description = "Google Cloud project that owns the VPC."
}

variable "region" {
  type        = string
  description = "Region of the subnet and NAT."
}

variable "name" {
  type        = string
  description = "Name prefix, e.g. agents-dev."
}

variable "subnet_cidr" {
  type        = string
  description = "Primary range for nodes."
}

variable "pods_cidr" {
  type        = string
  description = "Secondary range for pod IPs."
}

variable "services_cidr" {
  type        = string
  description = "Secondary range for Kubernetes service IPs."
}

variable "enable_nat" {
  type        = bool
  default     = false
  description = "Create Cloud Router and NAT. Required when GKE nodes are private."
}

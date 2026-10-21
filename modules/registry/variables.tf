variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "name" {
  type        = string
  description = "Repository ID, e.g. agents-dev."
}

variable "immutable_tags" {
  type        = bool
  default     = false
  description = "true = a pushed tag can never be overwritten (recommended for production)."
}

variable "untagged_retention_days" {
  type    = number
  default = 14
}

variable "keep_recent_versions" {
  type    = number
  default = 20
}

variable "labels" {
  type    = map(string)
  default = {}
}

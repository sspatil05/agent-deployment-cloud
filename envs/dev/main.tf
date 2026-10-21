# DEV: cheapest shape. Zonal cluster = 1 managed control plane ("master") + 2 workers in one zone.
terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Shared state: create a bucket first, then uncomment and run `terraform init -migrate-state`.
  # backend "gcs" {
  #   bucket = "<state-bucket>"
  #   prefix = "agents/dev"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

module "platform" {
  source = "../../modules/platform"

  project_id        = var.project_id
  environment       = "dev"
  github_repository = var.github_repository
  region            = var.region

  # Control plane + 2 workers in a single zone.
  location         = "asia-south1-a"
  workers_per_zone = 2
  machine_type     = "e2-medium"

  # Own VPC for dev.
  subnet_cidr   = "10.50.0.0/20"
  pods_cidr     = "10.60.0.0/16"
  services_cidr = "10.70.0.0/20"

  # Cheap and simple: public node IPs (no NAT), open API, easy teardown.
  enable_private_nodes = false
  authorized_networks  = var.authorized_networks
  deletion_protection  = false
  release_channel      = "REGULAR"
  immutable_image_tags = false
}

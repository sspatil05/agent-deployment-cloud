# PROD: regional cluster (highly available control plane) with 2 workers, one in each of two zones.
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

  # backend "gcs" {
  #   bucket = "<state-bucket>"
  #   prefix = "agents/prod"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

module "platform" {
  source = "../../modules/platform"

  project_id        = var.project_id
  environment       = "prod"
  github_repository = var.github_repository
  region            = var.region

  # Regional control plane. 1 worker in each of 2 zones = 2 workers that survive the loss of one zone.
  location         = var.region
  node_locations   = ["asia-south1-a", "asia-south1-b"]
  workers_per_zone = 1
  machine_type     = "e2-standard-4"

  # Own VPC for prod (does not overlap dev or stage).
  subnet_cidr   = "10.52.0.0/20"
  pods_cidr     = "10.62.0.0/16"
  services_cidr = "10.72.0.0/20"
  master_cidr   = "172.17.0.32/28"

  # Locked down: private nodes, API reachable only from approved CIDRs, protected, stable upgrades.
  enable_private_nodes        = true
  authorized_networks         = var.authorized_networks
  require_authorized_networks = true
  deletion_protection         = true
  release_channel             = "STABLE"
  immutable_image_tags        = true
}

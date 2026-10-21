# STAGE: production-like behaviour at small scale. Zonal cluster, private nodes, protected from deletion.
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
  #   prefix = "agents/stage"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

module "platform" {
  source = "../../modules/platform"

  project_id        = var.project_id
  environment       = "stage"
  github_repository = var.github_repository
  region            = var.region

  # Control plane + 2 workers in a single zone.
  location         = "asia-south1-a"
  workers_per_zone = 2
  machine_type     = "e2-standard-2"

  # Own VPC for stage (does not overlap dev or prod).
  subnet_cidr   = "10.51.0.0/20"
  pods_cidr     = "10.61.0.0/16"
  services_cidr = "10.71.0.0/20"
  master_cidr   = "172.17.0.16/28"

  # Private nodes behind Cloud NAT, like production.
  enable_private_nodes = true
  authorized_networks  = var.authorized_networks
  deletion_protection  = true
  release_channel      = "REGULAR"
  immutable_image_tags = true
}

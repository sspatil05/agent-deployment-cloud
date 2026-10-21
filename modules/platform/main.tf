# One complete agent platform for one environment: APIs, its own VPC, a GKE cluster and an image registry.
# Every environment calls this module with different inputs, so dev, stage and prod stay structurally identical.

locals {
  name = "agents-${var.environment}"
  labels = merge(var.labels, {
    environment = var.environment
    workload    = "ai-agents"
    managed_by  = "terraform"
  })
}

resource "google_project_service" "apis" {
  for_each = toset([
    "artifactregistry.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "compute.googleapis.com",
    "connectgateway.googleapis.com",
    "container.googleapis.com",
    "gkehub.googleapis.com",
    "iam.googleapis.com",
  ])
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

module "vpc" {
  source = "../vpc"

  project_id    = var.project_id
  region        = var.region
  name          = local.name
  subnet_cidr   = var.subnet_cidr
  pods_cidr     = var.pods_cidr
  services_cidr = var.services_cidr
  enable_nat    = var.enable_private_nodes

  depends_on = [google_project_service.apis]
}

module "gke" {
  source = "../gke"

  project_id          = var.project_id
  name                = "${local.name}-cluster"
  location            = var.location
  node_locations      = var.node_locations
  network_id          = module.vpc.network_id
  subnet_id           = module.vpc.subnet_id
  pods_range_name     = module.vpc.pods_range_name
  services_range_name = module.vpc.services_range_name

  release_channel             = var.release_channel
  enable_private_nodes        = var.enable_private_nodes
  master_cidr                 = var.master_cidr
  authorized_networks         = var.authorized_networks
  require_authorized_networks = var.require_authorized_networks
  deletion_protection         = var.deletion_protection
  enable_fleet                = var.enable_connect_gateway

  workers_per_zone = var.workers_per_zone
  machine_type     = var.machine_type
  disk_size_gb     = var.disk_size_gb
  disk_type        = var.disk_type
  labels           = local.labels

  depends_on = [google_project_service.apis]
}

module "registry" {
  source = "../registry"

  project_id     = var.project_id
  region         = var.region
  name           = local.name
  immutable_tags = var.immutable_image_tags
  labels         = local.labels

  depends_on = [google_project_service.apis]
}

# GitHub Actions deployer for this environment (skipped when github_repository is empty).
module "github_actions" {
  count  = var.github_repository == "" ? 0 : 1
  source = "../github-actions"

  project_id             = var.project_id
  name                   = local.name
  github_repository      = var.github_repository
  github_environment     = var.environment
  registry_location      = var.region
  registry_id            = module.registry.repository_id
  enable_connect_gateway = var.enable_connect_gateway
}

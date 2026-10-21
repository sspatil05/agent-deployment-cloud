# A GKE cluster with one Google-managed control plane (the "master") and a single worker node pool.
# Zonal cluster:    location = a zone,   workers_per_zone = 2                      => 2 workers, 1 zone
# Regional cluster: location = a region, node_locations = [2 zones], per zone = 1  => 2 workers, HA control plane

# Dedicated least-privilege identity for the worker nodes (instead of the default compute account).
resource "google_service_account" "nodes" {
  account_id   = "${var.name}-nodes"
  display_name = "GKE worker nodes for ${var.name}"
  project      = var.project_id
}

resource "google_project_iam_member" "nodes" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/artifactregistry.reader",
  ])
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.nodes.email}"
}

resource "google_container_cluster" "this" {
  name           = var.name
  project        = var.project_id
  location       = var.location
  node_locations = var.node_locations

  network    = var.network_id
  subnetwork = var.subnet_id

  # The worker pool is managed separately below, so the default pool is removed.
  remove_default_node_pool = true
  initial_node_count       = 1

  deletion_protection = var.deletion_protection
  resource_labels     = var.labels

  # eBPF dataplane with built-in NetworkPolicy support.
  datapath_provider = "ADVANCED_DATAPATH"

  release_channel {
    channel = var.release_channel
  }

  ip_allocation_policy {
    cluster_secondary_range_name  = var.pods_range_name
    services_secondary_range_name = var.services_range_name
  }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  private_cluster_config {
    enable_private_nodes    = var.enable_private_nodes
    enable_private_endpoint = false
    master_ipv4_cidr_block  = var.enable_private_nodes ? var.master_cidr : null
  }

  dynamic "master_authorized_networks_config" {
    for_each = length(var.authorized_networks) > 0 ? [1] : []
    content {
      dynamic "cidr_blocks" {
        for_each = var.authorized_networks
        content {
          cidr_block   = cidr_blocks.value.cidr
          display_name = cidr_blocks.value.name
        }
      }
    }
  }

  # Register with the fleet so CI can reach the cluster through the Connect gateway (no network path needed).
  dynamic "fleet" {
    for_each = var.enable_fleet ? [1] : []
    content {
      project = var.project_id
    }
  }

  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS"]
  }

  lifecycle {
    precondition {
      condition     = !var.require_authorized_networks || length(var.authorized_networks) > 0
      error_message = "This environment requires authorized_networks: list the CIDRs allowed to reach the Kubernetes API."
    }
  }
}

resource "google_container_node_pool" "workers" {
  name     = "workers"
  project  = var.project_id
  cluster  = google_container_cluster.this.name
  location = var.location

  node_count = var.workers_per_zone

  node_config {
    machine_type    = var.machine_type
    disk_size_gb    = var.disk_size_gb
    disk_type       = var.disk_type
    service_account = google_service_account.nodes.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
    labels          = var.labels

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  # Bring a new node up before taking one down, so upgrades never remove capacity.
  upgrade_settings {
    strategy        = "SURGE"
    max_surge       = 1
    max_unavailable = 0
  }

  depends_on = [google_project_iam_member.nodes]
}

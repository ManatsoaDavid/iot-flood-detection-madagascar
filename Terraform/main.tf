terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# ── IP statique externe ──────────────────────────────────────
resource "google_compute_address" "iot_static_ip" {
  name   = "iot-mada-static-ip"
  region = var.region
}

# ── Règles firewall ──────────────────────────────────────────
resource "google_compute_firewall" "iot_ports" {
  name    = "allow-iot-services"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22", "1883", "8883", "1880", "8080", "9090"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["iot-server"]
}

# ── VM principale ────────────────────────────────────────────
resource "google_compute_instance" "iot_server" {
  name         = "iot-flood-mada-server"
  machine_type = var.machine_type
  zone         = var.zone
  tags         = ["iot-server"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 20
      type  = "pd-standard"
    }
  }

  network_interface {
    network = "default"
    access_config {
      nat_ip = google_compute_address.iot_static_ip.address
    }
  }

  metadata = {
    ssh-keys = "${var.ssh_user}:${file(var.ssh_pub_key_path)}"
  }

  labels = {
    project = "iot-inondation"
    pays    = "madagascar"
  }
}

# ── Bucket GCS pour backup des données ──────────────────────
resource "google_storage_bucket" "iot_data_backup" {
  name          = "${var.project_id}-iot-flood-data"
  location      = var.region
  force_destroy = true

  lifecycle_rule {
    condition { age = 30 }
    action    { type = "Delete" }
  }
}
variable "project_id" {
  description = "ID du projet GCP"
  type        = string
  default     = "iot-flood-madagascar"
}

variable "region" {
  description = "Région GCP"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Zone GCP"
  type        = string
  default     = "us-central1-a"
}

variable "machine_type" {
  description = "Type de machine Compute Engine"
  type        = string
  default     = "e2-small"
}

variable "ssh_user" {
  description = "Utilisateur SSH"
  type        = string
  default     = "david"
}

variable "ssh_pub_key_path" {
  description = "Chemin clé SSH publique"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}
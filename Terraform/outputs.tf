output "vm_ip_externe" {
  description = "IP publique de la VM IoT"
  value       = google_compute_address.iot_static_ip.address
}

output "ssh_command" {
  description = "Commande SSH pour se connecter"
  value       = "ssh ${var.ssh_user}@${google_compute_address.iot_static_ip.address}"
}

output "thingsboard_url" {
  description = "URL ThingsBoard"
  value       = "http://${google_compute_address.iot_static_ip.address}:8080"
}

output "nodered_url" {
  description = "URL Node-RED"
  value       = "http://${google_compute_address.iot_static_ip.address}:1880"
}

output "mqtt_broker" {
  description = "Adresse du broker MQTT"
  value       = "${google_compute_address.iot_static_ip.address}:1883"
}
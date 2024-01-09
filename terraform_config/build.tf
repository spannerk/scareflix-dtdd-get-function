resource "google_cloudbuildv2_repository" "this-repository" {
  name = var.repo
  parent_connection = var.connection_id
  remote_uri = var.repo_uri
  location = var.region
}

resource "google_cloudbuild_trigger" "repo-trigger" {
  location = var.region
  name = var.repo

  repository_event_config {
    repository = google_cloudbuildv2_repository.this-repository.id
    push {
      branch = "main"
    }
  }

  filename = "cloudbuild.yaml"
}
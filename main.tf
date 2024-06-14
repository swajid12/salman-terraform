provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_cloudfunctions_function" "function" {
  name        = var.function_name
  runtime     = var.runtime
  entry_point = var.entry_point

  source_repository {
    url    = var.github_repo_url
    branch = var.github_repo_branch
    dir    = var.source_subdirectory
  }

  trigger_http = var.trigger_http

  available_memory_mb   = 256
  timeout               = 60

  # Optional environment variables
  # environment_variables = {
  #   key = "value"
  # }
}

output "function_name" {
  value = google_cloudfunctions_function.function.name
}

output "function_url" {
  value = google_cloudfunctions_function.function.https_trigger_url
}

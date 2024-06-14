variable "project_id" {
  description = "The ID of the project in which to create the function"
  type        = string
}

variable "region" {
  description = "The region in which to create the function"
  type        = string
  default     = "us-central1"
}

variable "function_name" {
  description = "The name of the cloud function"
  type        = string
}

variable "entry_point" {
  description = "The name of the function (as defined in source code) that will be executed"
  type        = string
}

variable "runtime" {
  description = "The runtime environment for the cloud function"
  type        = string
  default     = "nodejs14"
}

variable "github_repo_url" {
  description = "The URL of the GitHub repository containing the function code"
  type        = string
}

variable "github_repo_branch" {
  description = "The branch of the GitHub repository to deploy from"
  type        = string
  default     = "main"
}

variable "trigger_http" {
  description = "Boolean to determine if the function should be triggered by HTTP"
  type        = bool
  default     = true
}

variable "source_subdirectory" {
  description = "The subdirectory in the repo that contains the source code (if applicable)"
  type        = string
  default     = ""
}

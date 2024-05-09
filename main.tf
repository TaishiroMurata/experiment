terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.34.0"
    }
  }
}

provider "google" {
  project = "zuu-infra"
  region  = "asia-northeast1"
}

data "archive_file" "default" {
  type        = "zip"
  output_path = "./main.zip"
  source_dir  = "./src"
}

resource "google_storage_bucket" "default" {
  name                        = "murata-gcf-source"
  location                    = "asia-northeast1"
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "object" {
  name   = "${data.archive_file.default.output_md5}.zip"
  bucket = google_storage_bucket.default.name
  source = "/Users/taishiro.murata/learn-terraform-gcp/main.zip"
}


resource "google_cloudfunctions2_function" "default" {
  name        = "function-v4"
  location    = "asia-northeast1"
  description = "A new function"

  build_config {
    runtime     = "python39"
    entry_point = "main"
    source {
      storage_source {
        bucket = google_storage_bucket.default.name
        object = google_storage_bucket_object.object.name
      }
    }
  }

  service_config {
    max_instance_count    = 1
    available_memory      = "256M"
    timeout_seconds       = 60
    service_account_email = "biwa-tutorial@zuu-infra.iam.gserviceaccount.com"
  }
}

resource "google_cloud_run_service_iam_member" "member" {
  location = google_cloudfunctions2_function.default.location
  service  = google_cloudfunctions2_function.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "function_uri" {
  value = google_cloudfunctions2_function.default.service_config[0].uri
}

terraform {
  backend "s3" {
    bucket = "pigeon.pictures.hq"
    key    = "terraform/state/terraform.tfstate"
    region = "eu-central-1"
  }
}


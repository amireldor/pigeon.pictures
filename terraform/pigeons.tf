provider "aws" {
	region = "eu-central-1"
}

# I think this section is a secret! But it's now on GitHub. Oh well... better luck next project.
terraform {
	backend "s3" {
		bucket = "eize.ninja-private"
		key = "terraform/pigeon.pictures.tfstate"
		region = "eu-central-1"
	}
}

resource "aws_s3_bucket" "pigeons" {
	bucket = "pigeon.pictures"
	acl = "public-read"

	website {
		index_document = "index.html"
		error_document = "index.html"  # maybe make a redirect to "/index.html" document?
	}
}

resource "aws_route53_zone" "primary" {
	name = "pigeon.pictures."
}

resource "aws_route53_record" "master_pigeon" {
	zone_id = "${aws_route53_zone.primary.id}"
	name = "pigeon.pictures"
	type = "A"

	alias {
		name = "${aws_s3_bucket.pigeons.website_domain}"
		zone_id = "${aws_s3_bucket.pigeons.hosted_zone_id}"
		evaluate_target_health = true
	}
}

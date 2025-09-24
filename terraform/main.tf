
# -----------------------------------------------------------------------------
# PROVIDERS
# -----------------------------------------------------------------------------
provider "aws" {
  region = "eu-central-1"
}

provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

# -----------------------------------------------------------------------------
# DATA SOURCES
# -----------------------------------------------------------------------------
data "aws_caller_identity" "current" {}

# -----------------------------------------------------------------------------
# VARIABLES
# -----------------------------------------------------------------------------
variable "pixabay_api_key" {
  type        = string
  description = "The API key for Pixabay."
  sensitive   = true
}

# -----------------------------------------------------------------------------
# ACM CERTIFICATE (us-east-1, required for CloudFront custom domain)
# -----------------------------------------------------------------------------
resource "aws_acm_certificate" "pigeon_pictures" {
  provider          = aws.us_east_1
  domain_name       = "pigeon.pictures"
  validation_method = "DNS"
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate_validation" "pigeon_pictures" {
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.pigeon_pictures.arn
  validation_record_fqdns = [] # Fill with Route53 record FQDNs if automating DNS validation
}

output "pigeon_pictures_acm_arn" {
  value = aws_acm_certificate.pigeon_pictures.arn
}

# -----------------------------------------------------------------------------
# SECRETS MANAGER (Pixabay API Key)
# -----------------------------------------------------------------------------
resource "aws_secretsmanager_secret" "pixabay_api_key" {
  name        = "pigeon-pictures-pixabay-api-key"
  description = "API key for Pixabay used by the pigeon.pictures website"
}

resource "aws_secretsmanager_secret_version" "pixabay_api_key_version" {
  secret_id     = aws_secretsmanager_secret.pixabay_api_key.id
  secret_string = var.pixabay_api_key
}

# -----------------------------------------------------------------------------
# S3 BUCKET & WEBSITE CONFIGURATION
# -----------------------------------------------------------------------------
resource "aws_s3_bucket" "pigeon_pictures_bucket" {
  bucket = "pigeon.pictures"
}

resource "aws_s3_bucket_website_configuration" "pigeon_pictures_website" {
  bucket = aws_s3_bucket.pigeon_pictures_bucket.bucket

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_s3_object" "pixabay_svg" {
  bucket       = aws_s3_bucket.pigeon_pictures_bucket.id
  key          = "pigeons-2025/pixabay.svg"
  source       = "../src/assets/pixabay.svg"
  acl          = "public-read"
  content_type = "image/svg+xml"
}

# -----------------------------------------------------------------------------
# LAMBDA BUILD & DEPLOYMENT
# -----------------------------------------------------------------------------
resource "null_resource" "build_lambda" {
  triggers = {
    package_json_hash = filemd5("${path.module}/../src/lambda/package.json")
  }
  provisioner "local-exec" {
    command = "npm install --prefix ${path.module}/../src/lambda"
  }
}

data "archive_file" "lambda_zip" {
  depends_on  = [null_resource.build_lambda]
  type        = "zip"
  source_dir  = "${path.module}/../src/lambda"
  output_path = "${path.module}/../tmp/lambda.zip"
}

resource "aws_iam_role" "lambda_s3_put_role" {
  name = "pigeon-pictures-lambda-s3-put-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = { Service = "lambda.amazonaws.com" }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_s3_put_policy" {
  name        = "pigeon-pictures-lambda-s3-put-policy"
  description = "Allow Lambda to put objects in the pigeon.pictures bucket"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = ["s3:PutObject"],
        Resource = [
          "arn:aws:s3:::pigeon.pictures/pigeons-2025/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:eu-central-1:${data.aws_caller_identity.current.account_id}:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_put_policy_attach" {
  role       = aws_iam_role.lambda_s3_put_role.name
  policy_arn = aws_iam_policy.lambda_s3_put_policy.arn
}

resource "aws_lambda_function" "pigeons_lambda" {
  function_name    = "pigeon-pictures-update-pigeons"
  role             = aws_iam_role.lambda_s3_put_role.arn
  handler          = "index.handler"
  runtime          = "nodejs22.x"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 60
  memory_size      = 128
  environment {
    variables = {
      BUCKET_NAME     = aws_s3_bucket.pigeon_pictures_bucket.bucket
      PIXABAY_API_KEY = var.pixabay_api_key
    }
  }
}

# -----------------------------------------------------------------------------
# EVENTBRIDGE SCHEDULE FOR LAMBDA
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_event_rule" "pigeons_lambda_hourly" {
  name                = "pigeon-pictures-lambda-hourly"
  description         = "Triggers the pigeons Lambda every hour at 0 minutes"
  schedule_expression = "cron(0 * * * ? *)"
}

resource "aws_cloudwatch_event_target" "pigeons_lambda_target" {
  rule      = aws_cloudwatch_event_rule.pigeons_lambda_hourly.name
  target_id = "PigeonsLambdaTarget"
  arn       = aws_lambda_function.pigeons_lambda.arn
}

resource "aws_lambda_permission" "allow_eventbridge_invoke" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.pigeons_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.pigeons_lambda_hourly.arn
}

# -----------------------------------------------------------------------------
# CLOUDFRONT DISTRIBUTION
# -----------------------------------------------------------------------------
resource "aws_cloudfront_distribution" "pigeon_pictures_cdn" {
  origin {
    domain_name = aws_s3_bucket_website_configuration.pigeon_pictures_website.website_endpoint
    origin_id   = "pigeon-pictures-s3"
    origin_path = "/pigeons-2025"
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  aliases = ["pigeon.pictures"]

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "pigeon-pictures-s3"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.pigeon_pictures.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
}


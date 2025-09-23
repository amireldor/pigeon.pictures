# ACM certificate for pigeon.pictures (must be in us-east-1 for CloudFront)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}

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

# Output ACM certificate ARN for use in CloudFront
output "pigeon_pictures_acm_arn" {
  value = aws_acm_certificate.pigeon_pictures.arn
}

provider "aws" {
  region = "eu-central-1"
}

#########################
# Data Source for Account ID
#########################
data "aws_caller_identity" "current" {}

#########################
# Variable for Pixabay API Key
#########################
variable "pixabay_api_key" {
  type        = string
  description = "The API key for Pixabay."
  sensitive   = true
}

#########################
# Secrets Manager for PIXABAY_API_KEY
#########################
resource "aws_secretsmanager_secret" "pixabay_api_key" {
  name        = "pigeon-pictures-pixabay-api-key"
  description = "API key for Pixabay used by the pigeon.pictures website"
}

resource "aws_secretsmanager_secret_version" "pixabay_api_key_version" {
  secret_id     = aws_secretsmanager_secret.pixabay_api_key.id
  secret_string = var.pixabay_api_key
}

# The nice bucket
resource "aws_s3_bucket" "pigeon_pictures_bucket" {
  bucket = "pigeon.pictures"
}

# S3 static website configuration (recommended)
resource "aws_s3_bucket_website_configuration" "pigeon_pictures_website" {
  bucket = aws_s3_bucket.pigeon_pictures_bucket.bucket

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}


# Upload pixabay.svg asset to S3 at the desired key
resource "aws_s3_object" "pixabay_svg" {
  bucket       = aws_s3_bucket.pigeon_pictures_bucket.id
  key          = "pigeons-2025/pixabay.svg"
  source       = "../src/assets/pixabay.svg"
  acl          = "public-read"
  content_type = "image/svg+xml"
}

# A null resource to trigger the npm install command
resource "null_resource" "build_lambda" {
  # The trigger ensures this resource is "recreated" whenever the package.json changes.
  triggers = {
    package_json_hash = filemd5("${path.module}/../src/lambda/package.json")
  }

  # The local-exec provisioner runs a command on the machine executing Terraform.
  provisioner "local-exec" {
    command = "npm install --prefix ${path.module}/../src/lambda"
  }
}
#
# Package the lambda function into a zip file
data "archive_file" "lambda_zip" {
  depends_on  = [null_resource.build_lambda]
  type        = "zip"
  source_dir  = "${path.module}/../src/lambda"
  output_path = "${path.module}/../tmp/lambda.zip"
}

# Lambda IAM role for S3 PutObject
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

# Lambda function
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

  # ...existing code...
}

# EventBridge rule to trigger Lambda every hour at 0 minutes
resource "aws_cloudwatch_event_rule" "pigeons_lambda_hourly" {
  name                = "pigeon-pictures-lambda-hourly"
  description         = "Triggers the pigeons Lambda every hour at 0 minutes"
  schedule_expression = "cron(0 * * * ? *)"
}

# EventBridge target to connect rule to Lambda
resource "aws_cloudwatch_event_target" "pigeons_lambda_target" {
  rule      = aws_cloudwatch_event_rule.pigeons_lambda_hourly.name
  target_id = "PigeonsLambdaTarget"
  arn       = aws_lambda_function.pigeons_lambda.arn
}

# Allow EventBridge to invoke the Lambda
resource "aws_lambda_permission" "allow_eventbridge_invoke" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.pigeons_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.pigeons_lambda_hourly.arn
}



#########################
# IAM Role for CodeBuild (pigeon.pictures)
#########################
resource "aws_iam_role" "pigeon_codebuild_role" {
  name = "pigeon-pictures-codebuild-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = { Service = "codebuild.amazonaws.com" }
      }
    ]
  })
}

# Custom policy allowing S3 access only to the pigeon.pictures bucket.
resource "aws_iam_policy" "pigeon_codebuild_s3_policy" {
  name        = "pigeon-pictures-codebuild-s3-policy"
  description = "Allow CodeBuild to access and write to the pigeon.pictures bucket only"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid : "AllowS3AccessToPigeonPictures",
        Effect : "Allow",
        Action : [
          "s3:PutObject",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:ListBucket"
        ],
        Resource : [
          "arn:aws:s3:::pigeon.pictures",
          "arn:aws:s3:::pigeon.pictures/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "pigeon_codebuild_s3_policy_attach" {
  role       = aws_iam_role.pigeon_codebuild_role.name
  policy_arn = aws_iam_policy.pigeon_codebuild_s3_policy.arn
}

# Policy for CloudWatch Logs permissions
resource "aws_iam_policy" "pigeon_codebuild_cloudwatch_policy" {
  name        = "pigeon-pictures-codebuild-cloudwatch-policy"
  description = "Allow CodeBuild to create and write CloudWatch Logs for the pigeon.pictures project"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid : "AllowCloudWatchLogs",
        Effect : "Allow",
        Action : [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource : "arn:aws:logs:eu-central-1:${data.aws_caller_identity.current.account_id}:log-group:/aws/codebuild/pigeon-pictures-codebuild-project*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "pigeon_codebuild_cloudwatch_policy_attach" {
  role       = aws_iam_role.pigeon_codebuild_role.name
  policy_arn = aws_iam_policy.pigeon_codebuild_cloudwatch_policy.arn
}

resource "aws_iam_policy" "pigeon_codebuild_secrets_policy" {
  name        = "pigeon-pictures-codebuild-secrets-policy"
  description = "Allow CodeBuild to retrieve secret values from Secrets Manager for PIXABAY_API_KEY"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid : "AllowGetSecretValue",
        Effect : "Allow",
        Action : [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ],
        Resource : aws_secretsmanager_secret.pixabay_api_key.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "pigeon_codebuild_secrets_policy_attach" {
  role       = aws_iam_role.pigeon_codebuild_role.name
  policy_arn = aws_iam_policy.pigeon_codebuild_secrets_policy.arn
}

#############################
# CodeBuild Project for pigeon.pictures Website
#############################
resource "aws_codebuild_project" "pigeon_codebuild_project" {
  name          = "pigeon-pictures-codebuild-project"
  description   = "CodeBuild project for building and deploying the pigeon.pictures website, triggered by EventBridge schedule"
  build_timeout = 60

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/standard:5.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    # Inject the PIXABAY_API_KEY from Secrets Manager
    environment_variable {
      name  = "PIXABAY_API_KEY"
      value = aws_secretsmanager_secret.pixabay_api_key.arn
      type  = "SECRETS_MANAGER"
    }
  }

  service_role = aws_iam_role.pigeon_codebuild_role.arn

  source {
    type      = "GITHUB"
    location  = "https://github.com/amireldor/pigeon.pictures"
    buildspec = "buildspec.yml"
  }

  artifacts {
    type                   = "S3"
    location               = "pigeon.pictures"
    packaging              = "NONE"
    path                   = ""
    name                   = "astro-generated-website"
    override_artifact_name = true
    namespace_type         = "NONE"
    encryption_disabled    = true
  }
}

#########################################
# IAM Role for EventBridge (pigeon.pictures)
#########################################
resource "aws_iam_role" "pigeon_eventbridge_role" {
  name = "pigeon-pictures-eventbridge-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = { Service = "events.amazonaws.com" }
      }
    ]
  })
}

resource "aws_iam_role_policy" "pigeon_eventbridge_policy" {
  name = "pigeon-pictures-eventbridge-policy"
  role = aws_iam_role.pigeon_eventbridge_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "codebuild:StartBuild",
        Effect   = "Allow",
        Resource = aws_codebuild_project.pigeon_codebuild_project.arn
      }
    ]
  })
}

#########################################
# EventBridge Rule to Schedule the Build for pigeon.pictures
#########################################
resource "aws_cloudwatch_event_rule" "pigeon_codebuild_schedule" {
  name                = "pigeon-pictures-codebuild-schedule"
  description         = "Triggers the pigeon.pictures CodeBuild project every 60 minutes"
  schedule_expression = "cron(0/60 * * * ? *)"
}

#########################################
# EventBridge Target: Connect the Rule to the CodeBuild Project for pigeon.pictures
#########################################
resource "aws_cloudwatch_event_target" "pigeon_codebuild_target" {
  rule      = aws_cloudwatch_event_rule.pigeon_codebuild_schedule.name
  target_id = "PigeonPicturesCodeBuildTarget"
  arn       = aws_codebuild_project.pigeon_codebuild_project.arn
  role_arn  = aws_iam_role.pigeon_eventbridge_role.arn
}

# CloudFront distribution to serve from S3 bucket at /pigeons-2025
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


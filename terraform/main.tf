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
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid:    "AllowS3AccessToPigeonPictures",
        Effect: "Allow",
        Action: [
          "s3:PutObject",
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:ListBucket"
        ],
        Resource: [
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
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid:    "AllowCloudWatchLogs",
        Effect: "Allow",
        Action: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource: "arn:aws:logs:eu-central-1:${data.aws_caller_identity.current.account_id}:log-group:/aws/codebuild/pigeon-pictures-codebuild-project*"
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
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid:    "AllowGetSecretValue",
        Effect: "Allow",
        Action: [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ],
        Resource: aws_secretsmanager_secret.pixabay_api_key.arn
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
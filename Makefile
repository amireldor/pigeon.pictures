# Configuration
LAMBDA_NAME_FETCH = pigeon-images-fetcher
LAMBDA_NAME_DELETE = delete-old-pigeon-images
BUCKET_AWS_REGION = $(shell echo $$BUCKET_AWS_REGION)
BUCKET_NAME := $(shell echo $$BUCKET_NAME)
PIXABAY_API_KEY := $(shell echo $$PIXABAY_API_KEY)
IAM_ROLE_ARN := $(shell echo $$IAM_ROLE_ARN)
FETCH_DIR = fetch-pigeons
DELETE_DIR = delete-old
ZIP_FILE_FETCH = $(FETCH_DIR)/deployment.zip
ZIP_FILE_DELETE = $(DELETE_DIR)/deployment.zip
HANDLER_FETCH = pigeons.handler
HANDLER_DELETE = delete.handler
RUNTIME = nodejs22.x
# Add cron schedule expression for every 30 minutes (crontab format)
CRON_SCHEDULE = cron(*/30 * * * ? *)

# Install dependencies in the respective folders
install:
	cd $(FETCH_DIR) && npm install --omit=dev
	cd $(DELETE_DIR) && npm install --omit=dev

# Create deployment package for fetch-pigeons
package-fetch: install
	cd $(FETCH_DIR) && zip -r deployment.zip pigeons.mjs package.json node_modules

# Create deployment package for delete-old
package-delete: install
	cd $(DELETE_DIR) && zip -r deployment.zip delete.mjs package.json node_modules

# Deploy the fetch-pigeons Lambda function (creates new or updates existing)
deploy-fetch: package-fetch
	if aws lambda get-function --function-name $(LAMBDA_NAME_FETCH) >/dev/null 2>&1; then \
		aws lambda update-function-code --function-name $(LAMBDA_NAME_FETCH) --zip-file fileb://$(ZIP_FILE_FETCH); \
		aws lambda update-function-configuration --function-name $(LAMBDA_NAME_FETCH) \
			--timeout 30 \
			--memory-size 256 \
			--environment Variables="{BUCKET_AWS_REGION='$(BUCKET_AWS_REGION)',BUCKET_NAME='$(BUCKET_NAME)',PIXABAY_API_KEY='$(PIXABAY_API_KEY)'}"; \
	else \
		aws lambda create-function --function-name $(LAMBDA_NAME_FETCH) \
			--runtime $(RUNTIME) \
			--role $(IAM_ROLE_ARN) \
			--handler $(HANDLER_FETCH) \
			--timeout 30 \
			--memory-size 256 \
			--zip-file fileb://$(ZIP_FILE_FETCH) \
			--environment Variables="{BUCKET_AWS_REGION='$(BUCKET_AWS_REGION)',BUCKET_NAME='$(BUCKET_NAME)',PIXABAY_API_KEY='$(PIXABAY_API_KEY)'}"; \
	fi
	aws events put-rule \
		--name "$(LAMBDA_NAME_FETCH)-schedule" \
		--schedule-expression "$(CRON_SCHEDULE)"
	aws lambda add-permission \
		--function-name $(LAMBDA_NAME_FETCH) \
		--statement-id "$(LAMBDA_NAME_FETCH)-event" \
		--action 'lambda:InvokeFunction' \
		--principal events.amazonaws.com \
		--source-arn $$(aws events describe-rule --name "$(LAMBDA_NAME_FETCH)-schedule" --query 'Arn' --output text) 2>/dev/null || true
	aws events put-targets \
		--rule "$(LAMBDA_NAME_FETCH)-schedule" \
		--targets "Id"="1","Arn"="$$(aws lambda get-function --function-name $(LAMBDA_NAME_FETCH) --query 'Configuration.FunctionArn' --output text)"

# Deploy the delete-old Lambda function (creates new or updates existing)
deploy-delete: package-delete
	if aws lambda get-function --function-name $(LAMBDA_NAME_DELETE) >/dev/null 2>&1; then \
		aws lambda update-function-code --function-name $(LAMBDA_NAME_DELETE) --zip-file fileb://$(ZIP_FILE_DELETE); \
		aws lambda update-function-configuration --function-name $(LAMBDA_NAME_DELETE) \
			--timeout 30 \
			--memory-size 256 \
			--environment Variables="{BUCKET_AWS_REGION='$(BUCKET_AWS_REGION)',BUCKET_NAME='$(BUCKET_NAME)'}"; \
	else \
		aws lambda create-function --function-name $(LAMBDA_NAME_DELETE) \
			--runtime $(RUNTIME) \
			--role $(IAM_ROLE_ARN) \
			--handler $(HANDLER_DELETE) \
			--timeout 30 \
			--memory-size 256 \
			--zip-file fileb://$(ZIP_FILE_DELETE) \
			--environment Variables="{BUCKET_AWS_REGION='$(BUCKET_AWS_REGION)',BUCKET_NAME='$(BUCKET_NAME)'}"; \
	fi
	aws events put-rule \
		--name "$(LAMBDA_NAME_DELETE)-schedule" \
		--schedule-expression "$(CRON_SCHEDULE)"
	aws lambda add-permission \
		--function-name $(LAMBDA_NAME_DELETE) \
		--statement-id "$(LAMBDA_NAME_DELETE)-event" \
		--action 'lambda:InvokeFunction' \
		--principal events.amazonaws.com \
		--source-arn $$(aws events describe-rule --name "$(LAMBDA_NAME_DELETE)-schedule" --query 'Arn' --output text) 2>/dev/null || true
	aws events put-targets \
		--rule "$(LAMBDA_NAME_DELETE)-schedule" \
		--targets "Id"="1","Arn"="$$(aws lambda get-function --function-name $(LAMBDA_NAME_DELETE) --query 'Configuration.FunctionArn' --output text)"

# Update existing fetch-pigeons Lambda function code
update-fetch: package-fetch
	aws lambda update-function-code --function-name $(LAMBDA_NAME_FETCH) --zip-file fileb://$(ZIP_FILE_FETCH)

# Update existing delete-old Lambda function code
update-delete: package-delete
	aws lambda update-function-code --function-name $(LAMBDA_NAME_DELETE) --zip-file fileb://$(ZIP_FILE_DELETE)

# Clean up ZIP files
clean:
	rm -f $(ZIP_FILE_FETCH) $(ZIP_FILE_DELETE)

# Add new target to clean up EventBridge rules
clean-schedule:
	aws events remove-targets --rule "$(LAMBDA_NAME_FETCH)-schedule" --ids "1" || true
	aws events delete-rule --name "$(LAMBDA_NAME_FETCH)-schedule" || true
	aws events remove-targets --rule "$(LAMBDA_NAME_DELETE)-schedule" --ids "1" || true
	aws events delete-rule --name "$(LAMBDA_NAME_DELETE)-schedule" || true

.PHONY: install package-fetch package-delete deploy-fetch deploy-delete update-fetch update-delete clean clean-schedule
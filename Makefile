# Configuration
LAMBDA_NAME_FETCH = pigeon-images-fetcher
LAMBDA_NAME_DELETE = delete-old-pigeon-images
AWS_REGION = us-east-1
BUCKET_NAME = $(BUCKET_NAME)
PIXABAY_API_KEY = $(PIXABAY_API_KEY)
IAM_ROLE_ARN = $(IAM_ROLE_ARN)
FETCH_DIR = fetch-pigeons
DELETE_DIR = delete-old
ZIP_FILE_FETCH = $(FETCH_DIR)/deployment.zip
ZIP_FILE_DELETE = $(DELETE_DIR)/deployment.zip
HANDLER_FETCH = pigeons.handler
HANDLER_DELETE = delete.handler
RUNTIME = nodejs22.x

# Install dependencies in the respective folders
install:
	cd $(FETCH_DIR) && npm install --production
	cd $(DELETE_DIR) && npm install --production

# Create deployment package for fetch-pigeons
package-fetch: install
	cd $(FETCH_DIR) && zip -r deployment.zip pigeons.mjs package.json node_modules

# Create deployment package for delete-old
package-delete: install
	cd $(DELETE_DIR) && zip -r deployment.zip delete.mjs package.json node_modules

# Deploy the fetch-pigeons Lambda function (first-time deployment)
deploy-fetch: package-fetch
	aws lambda create-function --function-name $(LAMBDA_NAME_FETCH) \
	  --runtime $(RUNTIME) \
	  --role $(IAM_ROLE_ARN) \
	  --handler $(HANDLER_FETCH) \
	  --timeout 30 \
	  --memory-size 256 \
	  --zip-file fileb://$(ZIP_FILE_FETCH) \
	  --environment Variables="{AWS_REGION='$(AWS_REGION)',BUCKET_NAME='$(BUCKET_NAME)',PIXABAY_API_KEY='$(PIXABAY_API_KEY)'}"

# Deploy the delete-old Lambda function (first-time deployment)
deploy-delete: package-delete
	aws lambda create-function --function-name $(LAMBDA_NAME_DELETE) \
	  --runtime $(RUNTIME) \
	  --role $(IAM_ROLE_ARN) \
	  --handler $(HANDLER_DELETE) \
	  --timeout 30 \
	  --memory-size 256 \
	  --zip-file fileb://$(ZIP_FILE_DELETE) \
	  --environment Variables="{AWS_REGION='$(AWS_REGION)',BUCKET_NAME='$(BUCKET_NAME)'}"

# Update existing fetch-pigeons Lambda function code
update-fetch: package-fetch
	aws lambda update-function-code --function-name $(LAMBDA_NAME_FETCH) --zip-file fileb://$(ZIP_FILE_FETCH)

# Update existing delete-old Lambda function code
update-delete: package-delete
	aws lambda update-function-code --function-name $(LAMBDA_NAME_DELETE) --zip-file fileb://$(ZIP_FILE_DELETE)

# Clean up ZIP files
clean:
	rm -f $(ZIP_FILE_FETCH) $(ZIP_FILE_DELETE)

.PHONY: install package-fetch package-delete deploy-fetch deploy-delete update-fetch update-delete clean
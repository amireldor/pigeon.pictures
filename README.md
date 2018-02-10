Hello, this is [pigeon.pictures][1]. It shows pictures of pigeons and updates
every 30 minutes. It's not always pigeons (not intended), and that is funny.

This version currently uses AWS Lambda deployed with Zappa to call Google
Search API to get the images. It then generates an index.html and saves it to
an S3 Bucket which was supposed to be created earlier with Terraform. Terraform
also creates a Route53 zone for serving the bucket.

How to do things:
-----------------

Create a src/private.py from the template.

To deploy, you need to use Terraform first (see stuff in "/terraform" folder)
and then you need to run "zappa deploy" (which is installed as part of
requirements.txt) from inside "/src"). To update use "zappa update" but this is
not a Zappa guide. See their README.

[1]: http://pigeon.pictures

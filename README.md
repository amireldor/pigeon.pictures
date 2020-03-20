Hello, this is [pigeon.pictures][pp]. It shows pictures of pigeons and updates
every 30 minutes. It's not always pigeons (semi-not intended), and that is funny.

This version currently uses AWS Lambda deployed with Zappa to call Google
Search API to get the images. It then generates an index.html and saves it to
an S3 Bucket which was supposed to be created earlier with Terraform. Terraform
also creates a Route53 zone for serving the bucket.

How to do things:
-----------------

Define environment variables:

 - GOOGLE_CSE_ID
 - GOOGLE_API_KEY
 - S3_BUCKET_NAME

To deploy, you need to use Terraform first (see stuff in "/terraform" folder)
and then you need to run "zappa deploy" (installed via setup.py). To update use "zappa update" but this is not a Zappa guide. See their README.

[pp]: http://pigeon.pictures


I use [zappa][zappa] for deployment, so you need something like `zappa deploy` _or more likely:_ "`zappa update`" (for updating after deployment). Scheduling is done with deployment. Consider calling `zappa invoke production lambda.main` to initialize the first _index.html_ (I think you can omit "production").

This is Python 3 stuff, so do the `pip install -e .` magic.

[zappa]: https://www.zappa.io/

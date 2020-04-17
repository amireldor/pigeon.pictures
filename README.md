These are only clues to myself to what actually went on here.

---

Hello, this is [pigeon.pictures][pp]. It shows pictures of pigeons and updates
every 30 minutes. It's not always pigeons (semi-not intended), and that is funny.

This version currently uses AWS Lambda deployed with Serverless and calls the
flickr photo search API to get the images. It then generates an index.html and
saves it to an S3 Bucket which was supposed to be created earlier with
Terraform. Terraform also creates a Route53 zone for serving the bucket.

How to do things:
-----------------

Define environment variables:

 - `FLICKR_API_KEY`
 - `S3_BUCKET_NAME` (defaults to `pigeon.pictures`)

To deploy, you need to use Terraform first (see stuff in "/terraform" folder)
and then you need to run `sls deploy` (installed via setup.py). To update use `sls deploy` again, I think.  You can manually invoke things with `sls invoke -f pigeons`.

[pp]: http://pigeon.pictures


I use [serverless][lambda] for deployment, so you need something like `npm i -g serverless`
and then `serverless deploy` or something like that. Scheduling is done with the deployment.
Consider invoking the function somehow locally to initialize the first _index.html_.

Also: `sls plugin install -n serverless-python-requirements`

Or something like that.

This is Python 3 stuff, so do the `pip install -e .` magic to develop.

[lambda]: https://serverless.com


Tests
-----

`pytest`

To run manually, do `python -m pigeonpictures`

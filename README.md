(note: kinda updated, but I'm doing things)

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

---

Pictures of pigeons from the interwebs that change every 30 minutes (unless I chose something different someday).

I use [zappa][zappa] for deployment, so you need something like `zappa deploy` _or more likely:_ "`zappa update`" (for updating after deployment). Scheduling is done with deployment. Consider calling `zappa invoke production lambda.main` to initialize the first _index.html_ (I think you can omit "production").

This is Python 3 stuff, so do the `pip install -r requirements.txt` magic.

[zappa]: https://www.zappa.io/

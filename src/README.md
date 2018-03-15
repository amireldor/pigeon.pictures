pigeon.pictures
===============

Pictures of pigeons from the interwebs that change every 30 minutes (unless I chose something different someday).

I use [zappa][1] for deployment, so you need something like `zappa deploy` _or more likely:_ "`zappa update`" (for updating after deployment). Scheduling is done with deployment. Consider calling `zappa invoke production lambda.main` to initialize the first _index.html_ (I think you can omit "production").

This is Python 3 stuff, so do the `pip install -r requirements.txt` magic.

[1]: https://www.zappa.io/

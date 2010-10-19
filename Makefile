appserver=python2.5 /usr/local/bin/dev_appserver.py
appserver_args=--use_sqlite -d
appserver_dir=.

all:

run:
	$(appserver) $(appserver_args) $(appserver_dir)

run-clear:
	$(appserver) $(appserver_args) -c $(appserver_dir)

deploy:
	python2.5 /usr/local/bin/appcfg.py update .

# Copyright (C) 2009 KDS Software
include Makefile.def

# Targets
.PHONY: test clean dist todo

test: clean gitsubmodules nosetests

gitsubmodules:
	-git submodule add trac.khavr.com:/var/lib/git/tddspry tests/tddspry
	git submodule init
	git submodule update
	#fix for updating git submodules
	cd tests/tddspry; git pull origin master
	
nosetests:
	$(MAKE) -C $(app) build test

clean:
	-[ -d db ] && $(MAKE) -C db clean
	$(MAKE) -C $(app) clean
	-rm *~*
	-find . -name '*.pyc' -exec rm {} \;

dist: clean test #pylint
	$(MAKE) clean
	git tag -a -f -m "Making release $(ver)" rel-$(ver)
	git archive --prefix=$(proj)-$(ver)/ rel-$(ver) | bzip2 > ../$(proj)-$(ver).tar.bz2

deploy: dist
	scp ../$(proj)-$(ver).tar.bz2 deploy.sh $(deployto):
	ssh $(deployto) sh ./deploy.sh $(proj)-$(ver)
	./increment_version.py .version
	
pylint:
	pylint $(app) --max-public-methods=50 --method-rgx='[a-z_][a-z0-9_]{2,40}$$'

run:
	PYTHONPATH=$(PYTHON) $(app)/djcouchtest/manage.py runserver
   
syncdb:
	PYTHONPATH=$(PYTHON) $(app)/djcouchtest/manage.py syncdb --noinput
   
### Local variables: ***
### compile-command:"make" ***
### tab-width: 2 ***
### End: ***
# $Id:$
# Copyright (C) 2001-2008 KDS Software Group

include ../../Makefile.def

noseopt=-w .. --with-coverage --cover-package=django_couchdb --exe

modules=django_couchdb

.PHONY: test clean

test:
	PYTHONPATH=$(PYTHONPATH):. DJANGO_SETTINGS_MODULE=$(oquery_test_settings) nosetests  $(noseopt) $(modules)

clean:
	-rm *~*
	-rm *.pyc

### Local variables: ***
### compile-command:"make" ***
### tab-width: 2 ***
### End: ***
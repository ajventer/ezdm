PYTHON=`which python`
DESTDIR=/
BUILDIR=$(CURDIR)/debian/ezdm
PROJECT=ezdm
VERSION=0.0.1
PREFIX=usr

all:
		@echo "make source - Create source package"
		@echo "make install - Install on local system"
		@echo "make builddeb - Generate a debian package"
		@echo "make clean - Get rid of scratch and byte files"

source:
		$(PYTHON) setup.py sdist $(COMPILE)

install:
		$(PYTHON) setup.py install --prefix=/${PREFIX} --root $(DESTDIR) $(COMPILE) --record .install.record

uninstall:
		cat .install.record | sed s"#${PREFIX}#${DESTDIR}/${PREFIX}#g" | xargs rm -fv

builddeb:
		# build the source package in the parent directory
		# then rename it to project_version.orig.tar.gz
		$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=../ --prune
		rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*
		# build the package
		dpkg-buildpackage -i -I -rfakeroot
		
installdeb: builddeb
		dpkg -i ../ezdm_${VERSION}_all.deb

clean:
		$(PYTHON) setup.py clean
		rm -rf build/ MANIFEST
		find . -name '*.pyc' -delete

PYTHON=/usr/bin/python
DESTDIR=/
BUILDIR=$(CURDIR)/debian/ezdm
PROJECT=ezdm
VERSION=`head -n 1 debian/changelog | cut -d'(' -f2 | cut -d')' -f1`
PREFIX=usr

all:
		@echo "make source - Create source package"
		@echo "sudo make install - Install on local system"
		@echo "sudo make uninstall - Uninstall on local system"
		@echo "make builddeb - Generate a debian package"
		@echo "sudo make installdeb - Generate a debian package and install it"
		@echo "make clean - Get rid of scratch and byte files"

source:
		$(PYTHON) setup.py sdist $(COMPILE)
		
ppa: clean
		debuild -S | fgrep signfile | fgrep .changes | cut -d' ' -f3 > .changes_file
		cat .changes_file | sed "s#ezdm#../ezdm#g" | xargs dput ppa:ajventer/ezdm 

install:
		$(PYTHON) setup.py install --prefix=/${PREFIX} --root $(DESTDIR) $(COMPILE) --record .install.record --install-layout=deb

uninstall:
		cat .install.record | sed s"#${PREFIX}#${DESTDIR}/${PREFIX}#g" | xargs rm -fv

builddeb:
		# build the source package in the parent directory
		# then rename it to project_version.orig.tar.gz
		$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=../ --prune
		rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*
		# build the package
		debuild 
		
installdeb: builddeb
		sudo dpkg -i ../ezdm_${VERSION}_all.deb

clean:
		$(PYTHON) setup.py clean
		rm -rf build/ MANIFEST
		rm -fr debian/ezdm
		find . -name '*.pyc' -delete

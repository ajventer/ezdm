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
		debuild -S -I | fgrep signfile | fgrep .changes | cut -d' ' -f3 > .changes_file
		cat .changes_file | sed "s#ezdm#../ezdm#g" | xargs dput ppa:ajventer/ezdm 

install:
		$(PYTHON) setup.py install --prefix=/${PREFIX} --root $(DESTDIR) --install-scripts=/${PREFIX}/games/ --no-compile --force --record .install.record --install-layout=deb
		mkdir -p ${DESTDIR}/${PREFIX}/share/applications
		mkdir -p ${DESTDIR}/${PREFIX}/share/icons/hicolor/128x128/
		desktop-file-install dir=${DESTDIR}/${PREFIX}/share/applications/ ezdm.desktop 
		desktop-file-install dir=${DESTDIR}/${PREFIX}/share/applications/ ezdm-console.desktop 
		install -g root -o root -m 0666 ezdm.png ${DESTDIR}/${PREFIX}/share/icons/hicolor/128x128/ezdm.png
		install -g root -o root -m 0666 ezdm-console.png ${DESTDIR}/${PREFIX}/share/icons/hicolor/128x128/ezdm-console.png
		update-desktop-database

uninstall:
		cat .install.record | sed s"#${PREFIX}#${DESTDIR}/${PREFIX}#g" | xargs rm -fv

builddeb: clean
		# build the source package in the parent directory
		# then rename it to project_version.orig.tar.gz
		$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=../ --prune
		rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*
		# build the package
		debuild -I
		
installdeb: builddeb
		sudo dpkg -i ../ezdm_${VERSION}_all.deb

clean:
		$(PYTHON) setup.py clean
		rm -rf build/ MANIFEST
		rm -fr debian/ezdm
		find . -name '*.pyc' -delete

#!/usr/bin/env python

from distutils.core import setup
from check_code import script_list

setup(name='EZDM',
      version='1.0',
      description='Simple tools for helping dungeon masters with ADN&D games',
      author='A.J. Venter',
      license='GPLv3',
      author_email='ajventer@gmail.com',
      url='https://github.com/ajventer/ezdm',
      scripts=script_list(),
      packages=['ezdm_libs'],
      package_dir={'ezdm_libs': 'ezdm_libs'},
      package_data={'ezdm_libs': ['adnd2e/*', 'COPYING.html']}
      )

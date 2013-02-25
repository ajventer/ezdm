#!/usr/bin/env python

from distutils.core import setup

setup(name='EZDM',
      version='1.0',
      description='Simple tools for helping dungeon masters with ADN&D games',
      author='A.J. Venter',
      license='GPLv3',
      author_email='ajventer@gmail.com',
      url='https://github.com/ajventer/ezdm',
      scripts=['mkcs','xp_tool','quick_combat','ezdm','viewchar','dice_roller'],
      packages=['ezdm_libs'],
      package_dir={'ezdm_libs':'ezdm_libs'},
      package_data={'ezdm_libs':['adnd2e/*']},
     )

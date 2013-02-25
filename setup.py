#!/usr/bin/env python

from distutils.core import setup

setup(name='EZDM',
      version='1.0',
      description='Simple tools for helping dungeon masters with ADN&D games',
      author='A.J. Venter',
      author_email='ajventer@gmail.com',
      url='https://github.com/ajventer/ezdm',
      scripts=['dice_roller','mkcs','xp_tool','quick_combat','ezdm','viewchar'],
      packages=['ezdm.libs'],
      package_dir={'ezdm.libs':'ezdm.libs'},
      package_data={'ezdm.libs':['adnd2e/*']},
     )

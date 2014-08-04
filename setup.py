#!/usr/bin/env python

from setuptools import setup

setup(name='ezdm',
      depends=['simplejson', 'bottle', 'jinja2', 'setuptools'],
      version='2.0.0',
      description='Simple tools for helping dungeon masters with ADN&D games',
      author='A.J. Venter',
      license='GPLv3',
      author_email='ajventer@gmail.com',
      url='https://github.com/ajventer/ezdm',
      scripts=['ezdm'],
      packages=['ezdm_libs'],
      data_files=[('/etc/ezdm', ['etc/settings.py'])],
      package_dir={'ezdm_libs': 'ezdm_libs'},
      package_data={'ezdm_libs': ['adnd2e/*', 'characters/*', 'icons/*', 'items/*', 'maps/*', 'templates/*', 'avatars/*', 'tiles/*', 'backgrounds/*']}
      )

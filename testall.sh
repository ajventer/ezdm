#!/bin/bash
clear
nosetests --with-doctest --verbosity=3 --detailed-errors --with-coverage --cover-erase --doctest-options='+ELLIPSIS' -exe


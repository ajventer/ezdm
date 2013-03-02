#!/bin/bash
PROJECTDIR=`readlink -f $0`
PROJECTDIR=`dirname $PROJECTDIR`
CFGFILE="${PROJECTDIR}/.debchange"
if ! test -r ${CFGFILE} ; then
        echo -n  "Your full name ? "
        read DEBFULLNAME
        echo -n "Your e-mail ? "
        read DEBEMAIL
        echo "DEBFULLNAME=\"$DEBFULLNAME\"" > $CFGFILE
        echo "DEBEMAIL=\"$DEBEMAIL\"" >> $CFGFILE
fi
source $CFGFILE
export DEBFULLNAME
export DEBEMAIL
cd $PROJECTDIR
#If user did not give options - take text from last commit message
CHANGEOPTS=`git log | grep -vi "^author:" | grep -vi "^commit"  | grep -vi "^date:" | grep -vi "^$" | head -n 1`
CHANGEOPTS="$* $CHANGEOPTS"
BRANCH=`git branch | fgrep '*' | awk '{print $2}'`
CHANGEOPTS="$CHANGEOPTS -U $BRANCH"
echo $BRANCH
echo debchange $BRANCH - $CHANGEOPTS
echo debchange -r




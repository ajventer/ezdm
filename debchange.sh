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
if test $# -eq 0; then
        echo "No options or text given !"
        echo "I take the same options as debchange"
        exit 1
else
        CHANGEOPTS="$*"
fi
BRANCH=`git branch | fgrep '*' | awk '{print $2}'`
echo $BRANCH
debchange $BRANCH - $CHANGEOPTS
debchange -r




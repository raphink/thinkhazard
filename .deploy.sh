#!/bin/sh -xe

SSH_OPTS="-o StrictHostKeyChecking=no -i id_rsa"
SSH_HOST="reprepro@pkg.camptocamp.net"
SECTION="ci"
DISTRO="jessie/dev"
# TODO: Detect/generate that
PACKAGE_NAME="thinkhazard"
PACKAGE="${PACKAGE_NAME}_0.0_amd64.deb"

if [ -z $TRAVIS_TAG ]; then
  # TODO: pass $TRAVIS_TAG to make deb?
  make deb
  scp $SSH_OPTS $PACKAGE $SSH_HOST:/var/packages/apt/incoming
  ssh $SSH_OPTS $SSH_HOST "/usr/bin/reprepro -b /var/packages/apt -S ${SECTION} -P optional includedeb ${DISTRO} /var/packages/apt/incoming/${PACKAGE}"
else
  # TODO: Get that from tag
  NEW_DISTRO="jessie/staging"
  ssh $SSH_OPTS $SSH_HOST "/usr/bin/reprepro -b /var/packages/apt copy ${NEW_DISTRO} ${DISTRO} ${PACKAGE_NAME}"
fi

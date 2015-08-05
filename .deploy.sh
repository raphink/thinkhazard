#!/bin/sh -xe

SECTION="ci"
DISTRO="jessie/dev"
# TODO: Detect/generate that
PACKAGE_NAME="thinkhazard"
PACKAGE="${PACKAGE_NAME}_0.0_amd64.deb"

if [ -z $TRAVIS_TAG ]; then
  # TODO: pass $TRAVIS_TAG to make deb?
  make deb
  scp -o StrictHostKeyChecking=no -i id_rsa $PACKAGE reprepro@pkg.camptocamp.net:/var/packages/apt/incoming
  ssh -o StrictHostKeyChecking=no -i id_rsa reprepro@pkg.camptocamp.net "/usr/bin/reprepro -b /var/packages/apt -S ${SECTION} -P optional includedeb ${DISTRO} /var/packages/apt/incoming/${PACKAGE}"
else
  # TODO: Get that from tag
  NEW_DISTRO="jessie/staging"
  ssh -o StrictHostKeyChecking=no -i id_rsa reprepro@pkg.camptocamp.net "/usr/bin/reprepro -b /var/packages/apt copy ${NEW_DISTRO} ${DISTRO} ${PACKAGE_NAME}"
fi

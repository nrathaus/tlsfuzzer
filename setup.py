#!/usr/bin/env python

# Author: Hubert Kario
# Released under Gnu GPL v2.0, see LICENSE file for details

import os
import subprocess

# The version is derived from the git checkout so that it moves on its own,
# without anyone having to remember to bump it.  Consumers install this fork
# straight from a git URL, and pip compares only the version string, so a
# version that does not move means an installed copy is never replaced.
#
# Scheme: <year - 2020>.<month>.<day>, from the date of the most recent
# commit.  PEP 440 compares each field numerically, so the value increases
# with the date and leading zeros are normalised away -- 6.08.27 and 6.8.27
# are the same version.  Note that this has day granularity: a second commit
# on the same day produces the same version as the first, and consumers who
# already installed that day will not pick it up.
#
# _FALLBACK_VERSION is used when git is unavailable -- an unpacked sdist or
# a source tarball with no .git directory.
_FALLBACK_VERSION = "6.8.27"


def _git_version():
    """Derive a version from the git checkout, or return None."""
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        # not a `with` block and not check_output(): this file still has to
        # run under Python 2.6, where Popen is not a context manager and
        # check_output does not exist yet
        proc = subprocess.Popen(
            ["git", "log", "-1", "--format=%cd", "--date=format:%Y %m %d"],
            cwd=here,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.communicate()[0]
    except OSError:
        # no git binary on PATH
        return None
    if proc.returncode != 0:
        # not a git checkout
        return None
    fields = out.decode("ascii", "replace").split()
    if len(fields) != 3:
        return None
    try:
        year, month, day = (int(field) for field in fields)
    except ValueError:
        return None
    return "{0}.{1}.{2}".format(year - 2020, month, day)


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name="tlsfuzzer",
      version=_git_version() or _FALLBACK_VERSION,
      author="Hubert Kario",
      author_email="hkario@redhat.com",
      url="https://github.com/tlsfuzzer/tlsfuzzer",
      description="TLS test suite and fuzzer.",
      license="GPLv2",
      install_requires=["ecdsa >= 0.15", "tlslite-ng == 0.9.0b2"],
      extras_require={
          "analysis": [
              # Additionally to `tlsfuzzer.analysis`, this also satisfies the
              # following apps:
              # test_bleichenbacher_timing_marvin
              # test_lucky13
              # test_tls13_minerva
              # test_bleichenbacher_timing_pregenerate
              "matplotlib",
              "numpy",
              "pandas",
              "scipy",
          ],
          "execution": [
              "zstd",  # test_tls13_client_certificate_compression
          ],
          "extraction": [
              # Additionally to `tlsfuzzer.analysis`, this partially satisfies
              # the following apps:
              # test_bleichenbacher_timing_marvin
              # test_lucky13
              # test_tls13_minerva
              # test_bleichenbacher_timing_pregenerate
              "dpkt",
              "numpy",
              "pandas",
          ],
      },
      packages=["tlsfuzzer", "tlsfuzzer.utils"])

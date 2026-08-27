#!/usr/bin/env python

# Author: Hubert Kario
# Released under Gnu GPL v2.0, see LICENSE file for details

import os
import subprocess

# The version is derived from the git checkout so that it moves on every
# commit, without anyone having to remember to bump it.  Consumers install
# this fork straight from a git URL, and pip compares only the version
# string, so a version that does not move means an installed copy is never
# replaced.
#
# Scheme: <year - 2020>.<month>.<day>.<number of commits>.  Each field is
# compared numerically by PEP 440, so the value only ever increases: the
# date leads across days, and the commit count breaks ties between several
# commits landing on the same day.
#
# _FALLBACK_VERSION is used when git is unavailable -- an unpacked sdist or
# a source tarball with no .git directory.  It only needs to stay below any
# version this function returns.
_FALLBACK_VERSION = "6.8.27"


def _git(here, args):
    """Run git in `here`, returning its stdout, or None if that failed."""
    try:
        # not a `with` block and not check_output(): this file still has to
        # run under Python 2.6, where Popen is not a context manager and
        # check_output does not exist yet
        proc = subprocess.Popen(
            ["git"] + args, cwd=here,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.communicate()[0]
    except OSError:
        # no git binary on PATH
        return None
    if proc.returncode != 0:
        # not a git checkout
        return None
    return out.decode("ascii", "replace")


def _git_version():
    """Derive a version from the git checkout, or return None."""
    here = os.path.dirname(os.path.abspath(__file__))
    date = _git(here, ["log", "-1", "--format=%cd",
                       "--date=format:%Y %m %d"])
    count = _git(here, ["rev-list", "--count", "HEAD"])
    if date is None or count is None:
        return None
    fields = date.split() + count.split()
    if len(fields) != 4:
        return None
    try:
        year, month, day, commits = (int(field) for field in fields)
    except ValueError:
        return None
    return "{0}.{1}.{2}.{3}".format(year - 2020, month, day, commits)


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

#!/bin/sh
#
# Use this script to run your program LOCALLY.
#
# Note: Changing this script WILL NOT affect how CodeCrafters runs your program.
#
# Learn more: https://codecrafters.io/program-interface

set -e # Exit early if any commands fail

# Copied from .codecrafters/run.sh
#
# - Edit this to change how your program runs locally
# - Edit .codecrafters/run.sh to change how your program runs remotely

# we need set PATH = "/usr/bin:/usr/local/bin" in runtime session
#export PATH="/usr/bin:/usr/local/bin:$PATH"
exec python -u -m app.main "$@"

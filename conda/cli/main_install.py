# (c) 2012 Continuum Analytics, Inc. / http://continuum.io
# All Rights Reserved
#
# conda is distributed under the terms of the BSD 3-clause license.
# Consult LICENSE.txt or http://opensource.org/licenses/BSD-3-Clause.

from argparse import RawDescriptionHelpFormatter

from conda.anaconda import anaconda
from conda.planners import create_install_plan
from utils import add_parser_prefix, get_prefix, add_parser_yes


def configure_parser(sub_parsers):
    p = sub_parsers.add_parser(
        'install',
        formatter_class = RawDescriptionHelpFormatter,
        description     = "Install a list of packages into a specified Anaconda environment.",
        help            = "Install a list of packages into a specified Anaconda environment.",
        epilog          = activate_example,
    )
    add_parser_yes(p)
    p.add_argument(
        "--dry-run",
        action  = "store_true",
        default = False,
        help    = "display packages to be modified, without actually executing",
    )
    p.add_argument(
        '-f', "--file",
        action  = "store",
        help    = "filename to read package versions from",
    )
    add_parser_prefix(p)
    p.add_argument(
        "--progress-bar",
        action  = "store",
        default = "yes",
        choices = ["yes", "no"],
        help    = "display progress bar for package downloads (default: yes)",
    )
    p.add_argument(
        'packages',
        metavar = 'package_version',
        action  = "store",
        nargs   = '*',
        help    = "package versions to install into Anaconda environment",
    )
    p.set_defaults(func=execute)

def execute(args):
    pkg_versions = args.packages

    if len(pkg_versions) == 0 and not args.file:
        raise RuntimeError('too few arguments, must supply command line package specifications or --file')

    conda = anaconda()

    prefix = get_prefix(args)

    env = conda.lookup_environment(prefix)

    if args.file:
        try:
            req_strings = []
            with open(args.file) as fi:
                for line in fi:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        req_strings.append(line)
        except IOError:
            raise RuntimeError('could not read file: %s' % args.file)
    else:
        req_strings = pkg_versions

    for req_string in req_strings:
        if req_string.startswith('conda'):
            raise RuntimeError("package 'conda' may only be installed in the default environment")

    if len(req_strings) == 0:
        raise RuntimeError('no package specifications supplied')

    conda = anaconda()

    plan = create_install_plan(env, req_strings)

    if plan.empty():
        print 'All requested packages already installed into environment: %s' % prefix
        return

    print
    print "Package plan for installation in environment %s:" % prefix
    print plan

    if args.dry_run: return

    if not args.yes:
        proceed = raw_input("Proceed (y/n)? ")
        if proceed.lower() not in ['y', 'yes']:
            return

    plan.execute(env, args.progress_bar=="yes")


activate_example = '''
examples:
    conda install -n myenv scipy

'''

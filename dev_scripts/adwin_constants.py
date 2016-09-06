"""
adwin_constants.py [-h] [-R]

This script generates the file lib/ADwinsrc/globals.inc

Options:
    -h      Show this help
    -R      In addition to generating the include file, also
            replace all variable usages in the code with their
            synonyms.
            CAUTION: Works in place!
"""

from datetime import datetime
import os.path
import platform
import sys

root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path = [os.path.dirname(os.path.dirname(__file__))] + sys.path

from lib import config


def define_statements():
    for variable_category, variables in config.VARIABLES.items():
        if variables is None:
            continue
        if variable_category == 'fifo':
            variable_category = 'data'
        for name, number in variables.items():
            yield '#define {cat}_{name} {cat}_{number}'.format(
                cat=variable_category, name=name, number=number)

    for const_name, const_val in config.CONSTANTS['adwin'].items():
        yield '#define {} {}'.format(const_name, const_val)


def replace_tuples():
    for variable_category, variables in config.VARIABLES.items():
        if variables is None:
            continue
        if variable_category == 'fifo':
            variable_category = 'data'
        for name, number in variables.items():
            yield (
                '{cat}_{name}'.format(
                    cat=variable_category, name=name),
                '{cat}_{number}'.format(
                    cat=variable_category, number=number))

    for const_name, const_val in config.CONSTANTS['adwin'].items():
        if const_name.startswith('CASE_'):
            yield ('case {}'.format(const_name), 'case {}'.format(const_val))


def write_inc_file(outf):
    outf.write("")
    outf.write("'<ADbasic Header, Headerversion 001.001>\n")
    outf.write("'<Header End>\n")
    outf.write("' globals.inc\n")
    outf.write("' \n")
    outf.write("' ##################################################################\n")
    outf.write("' #            THIS FILE WAS AUTOMATICALLY GENERATED               #\n")
    outf.write("' #               EDIT BY HAND AT YOUR OWN PERIL                   #\n")
    outf.write("' ##################################################################\n")
    outf.write("' \n")
    outf.write("' Generated on {}\n".format(
        datetime.now().strftime('%a %d %b %Y at %R')))
    outf.write("' by {}@{} using {}\n".format(
        os.getlogin(),
        platform.node(),
        os.path.basename(__file__)))
    outf.write("\n")
    for def_stmnt in define_statements():
        outf.write("{}\n".format(def_stmnt))


def do_replace(srcdir):
    replacements = list(replace_tuples())

    srcfiles = [f for f in os.listdir(srcdir)
                if f.endswith('.bas') and f != 'globals.inc']

    for fn in srcfiles:
        with open(os.path.join(srcdir, fn), 'r+') as srcfobj:
            print('##### READING {}'.format(fn))
            new_lines = []
            n_changes = 0
            for linenum, line in enumerate(srcfobj):
                new_line = line
                for (new, old) in replacements:
                    if old in line:
                        new_line = new_line.replace(old, new)
                if line != new_line:
                    n_changes += 1
                    sys.stdout.write('{}:{}: {}'.format(fn, linenum + 1, new_line))
                new_lines.append(new_line)
            if n_changes > 0:
                print('## changing {} lines'.format(n_changes))
                srcfobj.seek(0)
                for line in new_lines:
                    srcfobj.write(line)
                srcfobj.truncate()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '-h':
            print(__doc__)
            sys.exit(0)
        elif sys.argv[1] == '-R':
            DO_REPLACE = True
        else:
            sys.stderr.write('Invalid usage!\n\n')
            sys.stderr.write(__doc__ + '\n')
            sys.exit(2)
    else:
        DO_REPLACE = False

    inc_filename_gold = os.path.join(root_dir, 'lib', 'ADwinsrc', 'globals.inc')
    inc_filename_goldII = os.path.join(root_dir, 'lib', 'goldII', 'globals.inc')
    
    print('Writing definitions to {}'.format(inc_filename_gold))
    with open(inc_filename_gold, 'w') as inc_file:
        write_inc_file(inc_file)
    
    print('Writing definitions to {}'.format(inc_filename_goldII))
    with open(inc_filename_goldII, 'w') as inc_file:
        write_inc_file(inc_file)

    if DO_REPLACE:
        do_replace(os.path.join(root_dir, 'lib', 'ADwinsrc'))
        do_replace(os.path.join(root_dir, 'lib', 'goldII'))

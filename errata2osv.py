import argparse
import os
import sys
from argparse import ArgumentParser

from models import *


def errata_to_osv(updateinfo, target_dir, ecosystem=None):
    """Convert errata to OSV entries"""
    """read updateinfo.xml file"""
    tree = ET.parse(updateinfo)
    errata = ErrataXMLView(tree.getroot())
    for errata_update in errata.updates:
        osv = OSVBugFromErrataUpdate(errata_update, ecosystem)
        osv_json_view = OSVBugJsonView(osv)
        osv_json_view.to_json_file(os.path.join(target_dir, osv.db_id + ".json"))


def main(sys_args):
    parser = ArgumentParser(description='errata to osv converter',
                            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('updateinfo', help='updateinfo xml with errata information')
    parser.add_argument('target_dir', help='target directory for output OSV entries')
    parser.add_argument('--ecosystem', help='OSV ecosystem of output OSV entries', default=None)
    args = parser.parse_args(sys_args)

    errata_to_osv(args.updateinfo, args.target_dir, args.ecosystem)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

"""
Removes tags with patient info from XML file and replaces patient names by
subject ids.

TODO:
- read XML
- map patient name to sid
- extract eye-laterality from <IMAGE_FILE_NAME>DOE_20121024_114922_OD_000000_SFA.tif</IMAGE_FILE_NAME>
- remove sensitive TAGS
- (re)add tag <PATIENT_ID>sid</PATIENT_ID>
- replace <IMAGE_FILE_NAME>DOE_20121024_114922_OD_000000_SFA.tif</IMAGE_FILE_NAME>
- replace xml-filename by <short_uid>-SFA.xml
   where short_uid = <sid-year-month-day-eye>
"""

import os, sys
import os.path as osp

# Set of tags to remove
TAGS = {'<LAST_NAME', '<GIVEN_NAME', '<MIDDLE_NAME', '<NAME_PREFIX',
        '<NAME_SUFFIX', '<FULL_NAME', '<BIRTH_DATE', '<PATIENT_ID',
        '<IMAGE_FILE_NAME'}


def is_sensitive(line):
    """Return true if line (in XML filed) starts with a sensitive TAG"""
    return any(line.startswith(t) for t in TAGS)


def remove_sensitive(lines):
    """Return iterator over lines skipping lines with sensitive data"""
    return (l for l in lines if not is_sensitive(l))


def sanitize_file(infilepath, outfilepath):
    """Copy sanitized from infilepath to outfilepath"""
    with open(outfilepath, 'w') as fout:
        lines = open(infilepath)
        for line in remove_sensitive(lines):
            fout.write(line)


def xmlfile_check(indir, outdir):
    """Return list of XML file names and check data/dir existance"""
    xmlfnames = [f for f in os.listdir(indir) if f.endswith('.xml')]
    if not xmlfnames:
        raise IOError('No .xml files in: ' + indir)
    if not osp.isdir(outdir):
        raise IOError('Output dir does not exist: ' + outdir)
    return xmlfnames


def run(indir, outdir):
    """Sanitized all XML files and indir and copy to outdir"""
    xmlfnames = xmlfile_check(indir, outdir)
    n = len(xmlfnames)
    print('sanitizing...')
    for i, xmlfname in enumerate(xmlfnames):
        infilepath = osp.join(indir, xmlfname)
        outfilepath = osp.join(outdir, xmlfname)
        print('%d of %d : %s -> %s' % (i + 1, n, xmlfname, outfilepath))
        sanitize_file(infilepath, outfilepath)
    print('done.')


if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) != 3:
        raise IOError('Expect input and output folder')
    _, indir, outdir = sys.argv
    run(indir, outdir)

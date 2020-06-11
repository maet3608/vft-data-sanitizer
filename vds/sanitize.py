"""
Removes tags with patient info from XML file and replaces patient names by
subject ids uses fuzzy matching between patient names in XML file and
the index database.
"""

import logging
import datetime
import fuzzy
import vds

import os, sys
import os.path as osp

logging.basicConfig(filename='sanitize.log',
                    filemode='w',
                    format='%(levelname)s : %(message)s',
                    level=logging.INFO)
logger = logging.getLogger('sanitizer')

error_counter = 0  # number file conversion errors
outpaths = set()  # Keep track of output files created

# Full name tags
SNTAG, ENTAG = '<FULL_NAME>', '</FULL_NAME>'

# Set of tags to remove. Note that full name will be replaced by sid
STAGS = {'<LAST_NAME', '<GIVEN_NAME', '<MIDDLE_NAME', '<NAME_PREFIX',
         '<NAME_SUFFIX', '<BIRTH_DATE', '<PATIENT_ID',
         '<IMAGE_FILE_NAME'}


def log_info(msg):
    """Log and print info messages"""
    print(msg)
    logger.info(msg)


def extract_patientname(filepath):
    """Extract full name from xml file"""
    with open(filepath) as f:
        for line in f:
            if line.startswith(SNTAG):
                name = line.strip().replace(SNTAG, '').replace(ENTAG, '')
                return name
    raise ValueError('No full patient name in ' + filepath)


def split_filename(filename):
    """Splits filenames of form DOE_20121024_114922_OD_000000_SFA.xml
    into their components and checks for validity"""
    name, ext = filename.split('.')
    try:
        sname, vdate, vtime, lat, sid, kind = name.split('_')
    except:
        raise ValueError('Invalid filename :' + filename)
    if ext != 'xml':
        raise ValueError('Not an .xml file :' + filename)
    if kind != 'SFA':
        raise ValueError('Not a SFA file :' + filename)
    if lat not in ['OD', 'OS']:
        raise ValueError('Unknown eye laterality :' + filename)
    if len(vdate) != 8:
        raise ValueError('Invalid visit date :' + filename)
    if len(vtime) != 6:
        raise ValueError('Invalid visit time :' + filename)
    return vdate, vtime, lat


def create_filename(sid, vdate, vtime, lat):
    """Creates an output filename with long uid based on components of
    input filename, e.g.
    DOE_20121024_114922_OD_000000_SFA.xml -> 000000-2012-10-24-11-49-22-OD.xml
    """
    y, o, d = vdate[:4], vdate[4:6], vdate[6:8]
    h, m, s = vtime[:2], vtime[2:4], vtime[4:6],
    uid = '%s-%s-%s-%s-%s-%s-%s' % (y, o, d, h, m, s, lat)
    filename = '%s-%s.xml' % (sid, uid)
    return filename


def is_sensitive(line):
    """Return true if line (in XML filed) starts with a sensitive TAG"""
    return any(line.startswith(t) for t in STAGS)


def remove_sensitive(lines):
    """Return iterator over lines skipping lines with sensitive data"""
    return (l for l in lines if not is_sensitive(l))


def sanitize_file(infilepath, outfilepath, sid):
    """Copy sanitized from infilepath to outfilepath"""
    with open(outfilepath, 'w') as fout:
        lines = open(infilepath)
        for line in remove_sensitive(lines):
            if line.startswith(SNTAG):  # fullname found
                line = '%s%s%s\n' % (SNTAG, sid, ENTAG)
            fout.write(line)


def name2sid(index, name, filename):
    """Map name to subject id using fuzzy matching"""
    match = fuzzy.find(name, index)
    logging.info('matches for %s : %s' % (name, str(match)))
    if match and match[0][1] > 1:
        return '%06d' % int(match[0][0])
    raise ValueError("Could not find sid for '%s' in %s" % (name, filename))


def sanitize(index, infilepath, outdir):
    """Remove sensitiv data and map name to id"""
    try:
        infilename = osp.basename(infilepath)
        name = extract_patientname(infilepath)
        sid = name2sid(index, name, infilename)
        vdate, vtime, lat = split_filename(infilename)

        outfilename = create_filename(sid, vdate, vtime, lat)
        outfilepath = osp.join(outdir, outfilename)
        if outfilepath in outpaths:
            raise ValueError('Duplicate output %s ' % outfilepath)
        outpaths.add(outfilepath)

        logging.info('writing %s' % outfilename)
        sanitize_file(infilepath, outfilepath, sid)
        return outfilename
    except Exception as e:
        global error_counter
        error_counter += 1
        logger.error(str(e))
        print(e)
        return str(e)


def xmlfile_check(indir, outdir):
    """Return list of XML filepaths and check data/dir existence"""
    infilepaths = []
    for path, dirs, files in os.walk(indir):
        fpaths = [osp.join(path, f) for f in files if f.endswith('_SFA.xml')]
        infilepaths.extend(fpaths)

    if not infilepaths:
        raise IOError('No .xml files in: ' + indir)
    if not osp.isdir(outdir):
        raise IOError('Output dir does not exist: ' + outdir)

    return infilepaths


def run(indexfile, indir, outdir):
    """Sanitized all XML files in indir and copy to outdir"""
    log_info('loading index ' + indexfile)
    index = fuzzy.create_index(indexfile)

    infilepaths = xmlfile_check(indir, outdir)
    n = len(infilepaths)
    log_info('processing %d files ...' % n)
    for i, infilepath in enumerate(infilepaths):
        logger.info('processing ' + infilepath)
        infilename = osp.basename(infilepath)
        outfilename = sanitize(index, infilepath, outdir)
        print('%d of %d : %s -> %s' % (i + 1, n, infilename, outfilename))

    log_info('finished with %d error(s)' % error_counter)


if __name__ == '__main__':
    log_info("running sanitizer version %s" % vds.__version__)

    now = datetime.datetime.now()
    logger.info('time of processing ' + now.strftime("%Y-%m-%d %H:%M"))

    try:
        logger.info('cmdline args: ' + ' '.join(sys.argv))
        if len(sys.argv) != 4:
            raise IOError('Expect index file, input and output folder')
        _, indexfile, indir, outdir = sys.argv
        run(indexfile, indir, outdir)
    except Exception as e:
        logger.error(str(e))
        print(e)

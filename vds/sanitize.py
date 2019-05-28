"""
Removes tags with patient info from XML file and replaces patient names by
subject ids uses fuzzy matching between patient names in XML file and
the index database.


- read lines of XML
- find <FULL_NAME or LAST_NAME', '<GIVEN_NAME', '<MIDDLE_NAME'
- create subject name
- fuzzy map to sid
- ensure that no sid is used twice!
- log errors
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
sids = dict()  # Keep track of subject ids used

# Set of tags to remove
STAGS = {'<LAST_NAME', '<GIVEN_NAME', '<MIDDLE_NAME', '<NAME_PREFIX',
         '<NAME_SUFFIX', '<FULL_NAME', '<BIRTH_DATE', '<PATIENT_ID',
         '<IMAGE_FILE_NAME'}


def log_info(msg):
    """Log and print info messages"""
    print(msg)
    logger.info(msg)


def extract_patientname(filepath):
    """Extract full name from xml file"""
    stag, etag = '<FULL_NAME>', '</FULL_NAME>'
    with open(filepath) as f:
        for line in f:
            if line.startswith(stag):
                name = line.strip().replace(stag, '').replace(etag, '')
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
    filename = '%06d-%s.xml' % (int(sid), uid)
    return filename


def is_sensitive(line):
    """Return true if line (in XML filed) starts with a sensitive TAG"""
    return any(line.startswith(t) for t in STAGS)


def remove_sensitive(lines):
    """Return iterator over lines skipping lines with sensitive data"""
    return (l for l in lines if not is_sensitive(l))


def sanitize_file(infilepath, outfilepath):
    """Copy sanitized from infilepath to outfilepath"""
    with open(outfilepath, 'w') as fout:
        lines = open(infilepath)
        for line in remove_sensitive(lines):
            fout.write(line)


def name2sid(index, name, filename):
    """Map name to subject id using fuzzy matching"""
    match = fuzzy.find(name, index)
    logging.info('matches for %s : %s' % (name, str(match)))
    if match and match[0][1] > 1:
        return match[0][0]
    raise ValueError("Could not find sid for '%s' in %s" % (name, filename))


def sanitize(index, indir, outdir, infilename):
    """Remove sensitiv data and map name to id"""
    try:
        infilepath = osp.join(indir, infilename)
        name = extract_patientname(infilepath)
        sid = name2sid(index, name, infilename)
        if sid in sids:
            raise ValueError('Duplicate sid %s : %s ' % (sids[sid], infilename))
        sids[sid] = (sid, infilename)

        vdate, vtime, lat = split_filename(infilename)
        outfilename = create_filename(sid, vdate, vtime, lat)
        outfilepath = osp.join(outdir, outfilename)

        sanitize_file(infilepath, outfilepath)
        return outfilename
    except Exception as e:
        global error_counter
        error_counter += 1
        logger.error(str(e))
        print(e)
        return str(e)


def xmlfile_check(indir, outdir):
    """Return list of XML file names and check data/dir existance"""
    xmlfnames = [f for f in os.listdir(indir) if f.endswith('.xml')]
    if not xmlfnames:
        raise IOError('No .xml files in: ' + indir)
    if not osp.isdir(outdir):
        raise IOError('Output dir does not exist: ' + outdir)
    return xmlfnames


def run(indexfile, indir, outdir):
    """Sanitized all XML files and indir and copy to outdir"""
    log_info('loading index ' + indexfile)
    index = fuzzy.create_index(indexfile)

    infilenames = xmlfile_check(indir, outdir)
    n = len(infilenames)
    log_info('processing %d files ...' % n)
    for i, infilename in enumerate(infilenames):
        logger.info('processing ' + infilename)
        outfilename = sanitize(index, indir, outdir, infilename)
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

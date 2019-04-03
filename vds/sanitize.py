"""
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


def show_file(filename):
    with open(filename) as f:
        for line in f:
            print(line, end='')


if __name__ == '__main__':
    filename = '../data/DOE_20121024_114922_OD_000000_SFA.xml'
    for line in remove_sensitive(open(filename)):
        print(line, end='')
    #show_file(filename)

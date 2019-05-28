# vft-data-sanitizer

Removes sensitive information from XML files containing visual field test data 
and replaces patient names by number ids using fuzzy matching.


# Installation

```
git clone https://github.com/maet3608/vft-data-sanitizer.git
cd vft-data-sanitizer
python setup.py develop
```


# Example

Run sanitize.py on example data.

```bash
cd vft-data-sanitizer/vds
python sanitize.py ../data/index.csv ../data ../out
```

Output should look like this

```bash
processing 2 files ...
1 of 2 : DOE_20121024_114922_OD_000000_SFA.xml -> 000011-2012-10-24-11-49-22-OD.xml
2 of 2 : DOE_20131118_092712_OD_00001_SFA.xml -> 000005-2013-11-18-09-27-12-OD.xml
finished with 0 error(s)
```

If there are any errors, please check the logfile `sanitize.log`


# Usage

```bash
cd vft-data-sanitizer/vds
python sanitize.py <csv_file_with_subject_ids> <folder_with_xml_files> <output_folder>
```
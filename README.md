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
python sanitize.py ../data ../out
```

Output should look like this

```bash
sanitizing...
1 of 2 : DOE_20121024_114922_OD_000000_SFA.xml -> ../out\DOE_20121024_114922_OD_000000_SFA.xml
2 of 2 : DOE_20131118_092712_OD_00001_SFA.xml -> ../out\DOE_20131118_092712_OD_00001_SFA.xml
done.
```


# Usage

```bash
cd vft-data-sanitizer/vds
python sanitize.py <folder_with_xml_files> <output_folder>
```
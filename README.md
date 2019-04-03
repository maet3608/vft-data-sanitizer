# vft-data-sanitizer

Removes sensitive information from XML files containing visual field test data 
and replaces patient names by number ids using fuzzy matching.


# Installation

```
git clone https://github.com/maet3608/vft-data-sanitizer.git
cd vft-data-sanitizer
python setup.py develop
```

# Usage

```
cd vft-data-sanitizer/vds
python sanitize.py <folder_with_xml_files> <output_folder>
```
# udb-reporting
Enhanced reporting from data in an Understand database.

Creates a static web site.


### requires
- linux
- [anaconda](https://www.anaconda.com/)
- [MkDocs](https://anaconda.org/conda-forge/mkdocs)
- [scitools Understand](https://scitools.com)
- [Uderstand Python api](https://scitools.com//support/python-api/)

### quick start example
```bash
# goto to cppcheck example directory
$ cd examples/cppcheck

# run application to build markdown docs
$ python ../../__main__.py

# run mkdocs to create site 
$ mkdocs build

# in browser open site/index.html
```

### installing
#### add to bottom of  ~/.profile
```bash
export PATH="$PATH:/home/ivv/local/bin:/home/ivv/software/scitools/bin/linux64"
export STI_HOME="/home/ivv/software/scitools"
export PYTHONPATH="/home/ivv/software/anaconda3/bin/python:/home/ivv/software/scitools/bin/linux64/Python"
```
#### create executable script ```udbreporting``` in /home/ivv/bin
- contents of ```udbreporting```
```bash
python /home/ivv/software/udb-reporting/__main__.py
mkdocs build
```

### running
* cd to directory containing
  - your_application.udb  (Understand database)
  - udb-report.yml (config file defining application type and reports to run)
  - base.yml (base config file for building mkdocs_ivory template static site)
  - mkdocs.yml (dynamically created config file for generating static site)
* run ```udbreporting``` executable script

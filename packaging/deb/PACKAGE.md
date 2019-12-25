* * *
# DEBIAN Package Creation Steps
* * *

## Infrastructure

* python3 -m venv p3_venv
* . p3_venv/bin/activate
* pip install -U pip setuptools stdeb
* pip install stdeb

## Package Creation

python3  setup_deb.py --command-packages=stdeb.command bdist_deb



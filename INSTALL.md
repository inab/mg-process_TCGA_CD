# Install instructions

* Python 2

```bash
virtualenv -p /usr/bin/python2 .py2Env
source .py2Env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
* Python3 (does not work due PyComps)

```bash
python3 -m venv .py3Env
source .py3Env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

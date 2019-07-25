# TCGA CD MuG/VRE wrapper install instructions

## Install the data and docker images used by the wrapper

* First, Docker must be installed and running in the machine. If it is not, you only have to run next command

 ```bash
 # These are pre-requisites for docker, described at https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-using-the-repository
 sudo apt update
 sudo apt install apt-transport-https ca-certificates curl software-properties-common
 curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
 sudo add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) \
    stable"
 
 # This is the docker package as such
 sudo apt update
 sudo apt install docker-ce
 ```

 Remember to add the username to the `docker` group, using for instance next recipe.

 ```bash
 sudo usermod -a -G docker $USER
 ```

* Second, download the code and from [TCGA benchmarking Dockers](https://github.com/inab/TCGA_benchmarking_dockers.git), generate the docker images and save the tag:

 ```bash
 THETAG=0.3.1
 git clone -b "$THETAG" https://github.com/inab/TCGA_benchmarking_dockers.git
 cd TCGA_benchmarking_dockers
 bash ./build.sh "$THETAG"
 cd ..
 cat > TCGA_CD.py.ini <<EOF
 [tcga_cd]
 docker_tag=$THETAG
 EOF
 ```

## Install the wrapper dependencies

* Python 2

```bash
virtualenv -p /usr/bin/python2 .py2Env
source .py2Env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
* Python3 (did not work in the past due PyComps)

```bash
python3 -m venv .py3Env
source .py3Env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```


# visidata-virtualrc

ingests virtualrc stream of entities into visidata
virtualrc-cmd within [visidata](https://www.visidata.org) will (not yet done) plot the second visible column of the current visidata sheet to virtualrc 

# use

i use virtualenv. thus git clone then

    virtualenv venv
    source venv/activate/bin
    pip install git+https://github.com/tobiasfeistmantl/python-actioncable-zwei.git&egg=ActionCableZwei
    pip3 install visidata

(per https://github.com/saulpw/visidata/blob/stable/README.md, and https://github.com/MementoMakoMori/VirtualSkiers/blob/master/Getting_Started.md)

Credentials from Registering a VirtualRC App [recurse.rctogether.com/apps](https://recurse.rctogether.com/apps) and create an app

i use bash to write a file that visidata expects
```commandline
cat > ~/.visidatarc << 'EOF'
import plugins.ingest_entities
options.virtualrc_app_id = 'YOURAPPID'
options.virtualrc_app_secret = 'YOURAPPSECRET'
EOF
```

which refers to a file `ingest_entities.py`  which visidata expects to be in `~/.visidata/plugins`, so symlink it to the plugin in this repo:

```commandline
mkdir -p ~/.visidata/plugins
ln -s ~/.visidata/plugins/ingest_entities.py `pwd`/plugins/ingest_entities.py
ls -al ~/.visidata/plugins/
```

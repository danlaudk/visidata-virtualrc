# visidata-virtualrc

ingests virtualrc stream of entities into visidata

`virtualrc-cmd` within [visidata](https://www.visidata.org) will plots the second visible column of the current visidata sheet to virtualrc 
`vertical-virtualrc-cmd` within visidata plots the first and only visible column of the current sheet of integers as vertical bars
# use

i use venv. thus git clone then

    python -m venv ./venv
    source venv/activate/bin
    pip install git+https://github.com/tobiasfeistmantl/python-actioncable-zwei.git&egg=ActionCableZwei
    pip3 install visidata

(per https://github.com/saulpw/visidata/blob/stable/README.md, and https://github.com/MementoMakoMori/VirtualSkiers/blob/master/Getting_Started.md)

Credentials from Registering a VirtualRC App [recurse.rctogether.com/apps](https://recurse.rctogether.com/apps) and create an app

i use bash to write a file that visidata expects
```commandline
cat > ~/.visidatarc << 'EOF'
import plugins.ingest_entities
options.virtualrc_app_id = 'YOUR_APP_ID'
options.virtualrc_app_secret = 'YOUR_APP_SECRET'
EOF
```

which refers to a file `ingest_entities.py`  which visidata expects to be in `~/.visidata/plugins`, so symlink it to the plugin in this repo:

```commandline
mkdir -p ~/.visidata/plugins
ln -s ~/.visidata/plugins/ingest_entities.py `pwd`/plugins/ingest_entities.py
ls -al ~/.visidata/plugins/
```

In addition to  the .visidatarc file, bc of library issues i'm too lazy to work out, I also need to have actioncable folder in this directory, and set
environment variables for appid as `export VIRTUALRCID=YOUR_APP_ID` and `EXPORT VIRTUALRCSEC=YOUR_SECRET`

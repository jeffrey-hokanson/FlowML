#! /bin/bash
# Start the IPython server

SCRIPT_PATH=${0%/*}
if [ "$0" != "$SCRIPT_PATH" ] && [ "$SCRIPT_PATH" != "" ]; then 
    cd $SCRIPT_PATH
fi

ipython notebook --certfile=mycert.pem --ipython-dir=ipython --profile=flowml_server

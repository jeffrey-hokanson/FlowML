#! /bin/bash
# Start the IPython server

SCRIPT_PATH=${0%/*}
if [ "$0" != "$SCRIPT_PATH" ] && [ "$SCRIPT_PATH" != "" ]; then 
    cd $SCRIPT_PATH
fi

export PYTHONPATH="$PWD:$PYTHONPATH"
ipython notebook --certfile=mycert.pem --ipython-dir=$PWD/ipython --profile=flowml_server 

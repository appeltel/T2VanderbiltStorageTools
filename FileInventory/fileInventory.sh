#!/bin/bash
PATH="/usr/local/bin:$PATH"
HOME=/home/appelte1
eval `/usr/local/bin/config_pkg -sh -a lio`
cd $HOME/T2VanderbiltStorageTools/FileInventory
/usr/local/lio/bin/lio_du -h -s @:/cms/store/ > $HOME/T2VanderbiltStorageTools/FileInventory/store.inv
/usr/local/lio/bin/lio_du -h -s @:/cms/store/user/ > $HOME/T2VanderbiltStorageTools/FileInventory/store.user.inv

/usr/local/bin/python reportFileInventory.py



# Create Debian Package:

    1. Create directory

    2. Create Subdirs
            - etc/bash_completion.d
            - usr/local/bin
            - usr/local/lib

    3. Move DEBIAN directory in:

        target/
            
            ... DEBIAN/control
                DEBIAN/postinst


    4. Move file artifacts in:

        target/

            * bash/xlines-completion.bash -->  etc/bash_completion.d/xlines-completion.bash
            * p3_venv/bin/xlines --> usr/local/bin/xlines
            * p3_venv/lib/python3.6/site-packages/xlines --> usr/local/lib/xlines
            * p3_venv/lib/python3.6/site-packages/xlines-0.7.15*  -->  usr/local/lib/xlines-0.7.15*
            * p3_venv/lib/python3.6/site-packages/pygments --> usr/local/lib/pygments
            * p3_venv/lib/python3.6/site-packages/Pygments-2.5.2.dist-info --> usr/local/lib/Pygments-2.5...
            
    5. Execute stdeb library on resulting directory to produce .deb archive


------------------------------------------------------------------------------------------

# Path to local modules:

```
def mapper(): 
"""Identifies path to python modules in virtual env"""
    for i in (6, 7, 8, 9): 
        path = 'p3_venv/lib/python3.' + str(i) + '/site-packages/'  
        if os.path.exists(path): 
            return path 
```


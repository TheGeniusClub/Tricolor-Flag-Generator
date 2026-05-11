# entry point

import sys
import os

# support both source run and pyinstaller bundle
if getattr(sys, 'frozen', False):
    # running in pyinstaller bundle
    bundle_dir = sys._MEIPASS
else:
    # running from source
    bundle_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, bundle_dir)

from src.ui import main

if __name__ == "__main__":
    main()

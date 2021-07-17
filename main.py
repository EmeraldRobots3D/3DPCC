import os
# os.environ['KIVY_WINDOW'] = 'pygame'
# os.environ['KIVY_TEXT'] = 'pygame'
# os.environ['KIVY_IMAGE'] = 'pygame'
import sys
import traceback

from gui.PCCApp import PCCApp

if __name__ == '__main__':
    try:
        app = PCCApp()
        app.run()
    except:
        app.stop()
        print("Exception in user code:")
        print("-" * 60)
        traceback.print_exc(file=sys.stdout)
        print("-" * 60)


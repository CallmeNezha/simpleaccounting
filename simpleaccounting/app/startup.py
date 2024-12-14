"""
    Copyright 2024- ZiJian Jiang @ https://github.com/CallmeNezha

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import os
import sys
from simpleaccounting.app.application import Application
import traceback


def trap_exc_during_debug(exc_type, exc_value, exc_traceback):
    # when app raises uncaught exception, print info
    print("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))


# install exception hook: without this, uncaught exception would cause application to exit
sys.excepthook = trap_exc_during_debug

if __name__ == "__main__":
    # Initialize the application
    os.environ['QT_SCALE_FACTOR'] = ''
    app = Application([])
    app.setQuitOnLastWindowClosed(True)
    app.exec_()
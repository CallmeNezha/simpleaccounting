#!/usr/bin/env python

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

import datetime
import pathlib
import sys
import subprocess
import qtpy

if __name__ == "__main__":
    #
    project_dir = pathlib.Path(__file__).parent.parent.absolute()
    package_dir = project_dir / "simpleaccounting"
    data_dir = project_dir / "data"
    icons_dir = data_dir / "icons"

    icons = sorted(im.relative_to(data_dir).as_posix() for im in icons_dir.glob('**/*.svg'))
    icons += sorted(im.relative_to(data_dir).as_posix() for im in icons_dir.glob('**/*.png'))

    from jinja2 import Template
    template = Template(
"""<!-- This qrc file is generated automatically on {{time}} -->
<RCC>
    <qresource>
        <!-- icons -->
        {%- for im in icons %}
        <file>{{ im }}</file>
        {%- endfor %}
    </qresource>
</RCC>
""")

    resource_qrc = template.render(icons=icons, time=datetime.datetime.now())
    qrc_path = data_dir / "resource.qrc"
    with open(qrc_path, 'w') as f:
        f.write(resource_qrc)

    if qtpy.PYSIDE6:
        if sys.platform == "win32":
            subprocess.run(["pyside6-rcc", "-o", package_dir / "resource.py", qrc_path],
                           cwd=data_dir,
                           check=True)
        else:
            subprocess.run(["pyside6-rcc", "-o", package_dir / "resource.py", qrc_path],
                           cwd=data_dir,
                           check=True)
    elif qtpy.PYQT6:
        if sys.platform == "win32":
            subprocess.run(["rcc", "-g", "python", "-o", package_dir / "resource.py", qrc_path],
                           cwd=data_dir,
                           check=True)
        else:
            subprocess.run(["rcc", "-g", "python", "-o", package_dir / "resource.py", qrc_path],
                           cwd=data_dir,
                           check=True)
    else:
        raise NotImplemented


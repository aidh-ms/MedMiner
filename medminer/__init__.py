"""
MedMiner

A Python package to extract mmedical information from text.

Modules:
- tasks: Contains classes for different tasks.
- tools: Contains classes for different tools for tasks.
- ui: Contains classes for user interface components.
- utils: Contains utility functions and classes.

Usage:
```python
from medminer.pipe import SingleAgentPipeline
from medminer.task.base import TaskRegistry
from medminer.utils.models import DefaultModel

reg = TaskRegistry()

pipe = SingleAgentPipeline(
    tasks=reg.all(),
    model=DefaultModel().model,
)

pipe.run(["Text to process"])
```

Author:
- Christian Porschen
- Paul Brauckmann

License:
```
MIT License

Copyright (c) 2025 AIDH MS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
"""

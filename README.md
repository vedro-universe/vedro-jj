# vedro-jj

[![Codecov](https://img.shields.io/codecov/c/github/vedro-universe/vedro-jj/master.svg?style=flat-square)](https://codecov.io/gh/vedro-universe/vedro-jj)
[![PyPI](https://img.shields.io/pypi/v/vedro-jj.svg?style=flat-square)](https://pypi.python.org/pypi/vedro-jj/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/vedro-jj?style=flat-square)](https://pypi.python.org/pypi/vedro-jj/)
[![Python Version](https://img.shields.io/pypi/pyversions/vedro-jj.svg?style=flat-square)](https://pypi.python.org/pypi/vedro-jj/)

[Vedro](https://vedro.io/) + [jj](https://pypi.org/project/jj/)

## Installation

<details open>
<summary>Quick</summary>
<p>

For a quick installation, you can use a plugin manager as follows:

```shell
$ vedro plugin install vedro-jj
```

</p>
</details>

<details>
<summary>Manual</summary>
<p>

To install manually, follow these steps:

1. Install the package using pip:

```shell
$ pip3 install vedro-jj
```

2. Next, activate the plugin in your `vedro.cfg.py` configuration file:

```python
# ./vedro.cfg.py
import vedro
import vedro_jj

class Config(vedro.Config):

    class Plugins(vedro.Config.Plugins):

        class VedroJJ(vedro_jj.VedroJJ):
            enabled = True
```

</p>
</details>

## Usage

```python
import httpx
import jj
import vedro
from jj.mock import mocked

class Scenario(vedro.Scenario):
    subject = "get users"

    def given(self):
        self.mock_matcher = jj.match("GET", "/users")
        self.mock_response = jj.Response(json=[])

    def when(self):
        with mocked(self.mock_matcher, self.mock_response):
            self.response = httpx.get("http://localhost:8080/users")

    def then(self):
        assert self.response.status_code == 200
        assert self.response.json() == []
```

```shell
$ vedro run
```

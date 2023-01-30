# ProductsUpPy

This is a simple Python wrapper around the ProductsUp platform API. It allows you to easily interact with the ProductsUp platform using Python code.

## Features

Easy to use interface
Support most ProductsUp platform API endpoints
Exception handling for common error cases

## Installation

You can install the package using pip:

```console
pip install productsup-py
```

## Usage

```python
import productsup_py as pu

# First, create a ProductUpAuth object
pu_auth = pu.ProductUpAuth(1234, 'mknjbhvgcd')
# Next, create a Projects object
example_project = pu.Projects(pu_auth)

project = example_project.get_project(28532)

print("Project ID:", project.project_id)
print("Project Name:", project.name)
print("Project Creation Date:", project.created_at)
```

``` console
Output:
Project ID: 28532
Project Name: Test
Project Creation Date: 2015-08-20 14:19:00
```

## Supporting

In case of any issues or for feature request, please raise an issue on the GitHub repository.

## License

Copyright (c) 2023, Lyes Tarzalt
All rights reserved.

This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.

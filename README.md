# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP24-003/orders/graph/badge.svg?token=7B9A593R95)](https://codecov.io/gh/CSCI-GA-2820-SP24-003/orders)
[![CI](https://github.com/CSCI-GA-2820-SP24-003/orders/actions/workflows/workflow.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP24-003/orders/actions)

## Overview

This project template contains starter code for your class project. The `/service` folder contains your `models.py` file for your model and a `routes.py` file for your service. The `/tests` folder has test case starter code for testing the model and the service separately. All you need to do is add your functionality. You can use the [lab-flask-tdd](https://github.com/nyu-devops/lab-flask-tdd) for code examples to copy from.

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.github/workflows   - Folder with Continuous Integration Support
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── routes.py              - module with service routes
├── common                 - common code package
|   ├── cli_commands.py    - Flask command to recreate all tables
|   ├── error_handlers.py  - HTTP error handling code
|   ├── log_handlers.py    - logging setup code
|   └── status.py          - HTTP status constants
└   models                 - module with business models
    ├── __init__.py        - model initializer
    ├── item.py            - item model
    ├── order.py           - order model
    ├── persistent_base.py - abstract model class

tests/                     - test cases package
├── __init__.py            - package initializer
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## Functions

These are the RESTful routes for `orders` and `items`
```
Endpoint          Methods  Rule
----------------  -------  -----------------------------------------------------
index             GET      /

list_orders       GET      /orders
create_orders     POST     /orders
get_orders        GET      /orders/<order_id>
update_orders     PUT      /orders/<order_id>
delete_orders     DELETE   /orders/<order_id>
ship_orders       PUT      /orders/<order_id>/ship

list_items        GET      /orders/<int:order_id>/items
create_items      POST     /orders/<order_id>/items
get_items         GET      /orders/<order_id>/items/<item_id>
update_items      PUT      /orders/<order_id>/items/<item_id>
delete_items      DELETE   /orders/<order_id>/items/<item_id>
```

The test cases have 95% test coverage and can be run with `pytest`

## License

Copyright (c) 2016, 2024 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.

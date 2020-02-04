# runcommand

script runs a command across a list of Aruba wireless controllers. iplist arg expects one IPv4 address per line.

example:

`runcommand "show ap database" controllers.txt`

usage:

```
usage: runcommand [-h] [--logging [{debug,warning}]] [--syn] [--decrypt]
                  cmd iplist

positional arguments:
  cmd                   command you want to run across controllers
  iplist                file containing IPv4 addresses of controllers

optional arguments:
  -h, --help            show this help message and exit
  --logging [{debug,warning}]
                        change logging output
  --syn                 connect to controllers one at a time
  --decrypt             runs encrypt disable before desired command
```

# local installation

## to install with pip:

- clone repository.

- from your terminal `cd` into root of the repository.

- run `python -m pip install .`

- you should now be able to run `runcommand` from your terminal

## to run but not install:

- clone repository. 

- from your terminal `cd` into root of the repository.

- run `python -m runcommand --help`

## to remove with pip:

- `python -m pip uninstall runcommand`

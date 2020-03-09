# runcommand

script can run a command or list of commands across a controller or list of controllers. please note that the netmiko platform is currently tied to ArubaOS only (`"aruba_os"`).

- iplist arg expects a file containing one IPv4 address per line.
- cmdlist arg expects a file containing one command per line.

usage examples:

- `runcommand -cmd "show ap database" -ip 192.168.1.2`
- `runcommand -cmd "show ap database" -iplist controllers.txt`
- `runcommand -cmdlist cmds.txt -ip 192.168.1.2`
- `runcommand -cmdlist cmds.txt -iplist controllers.txt`

very verbose debugging (enables netmiko/paramiko debug print statements):

- `runcommand -cmd "show ver" -ip 192.168.1.2 -logging debug`

script usage:

```
usage: runcommand [-h] [-logging [{debug,warning}]]
                   (-cmd CMD | -cmdlist CMDLIST) (-ip IP | -iplist IPLIST)
                   [--syn] [--decrypt] [-V]

exploratory project to run a command across a list of Aruba controllers and save the responses locally

optional arguments:
  -h, --help            show this help message and exit
  -logging [{debug,warning}]
                        change logging output
  -cmd CMD              command to run
  -cmdlist CMDLIST      file containing commands to run
  -ip IP                IPv4 address of controller
  -iplist IPLIST        file containing IPv4 addresses of controllers
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

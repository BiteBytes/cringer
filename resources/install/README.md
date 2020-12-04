# Install CSGO server

The installer starts with a fabric script that uploads several files to the server and install the required dependences and software on it. 

## Fabric

Fabric is a Python software that provides several server management utilities. It is tottally configurable using a Python script. The way to use it is giving a `fabfile.py` command and use the `fab` command. That fabfile.py has already been coded and is located at the same folder than this file. Inside of this script is defined the `prepare_server` command, to execute it you should use the `fab` command like this:

```
$ fab <command>:<parameter1>=<value1>, <parameter2>=<value2> -H <host> -u <user> -p <password> 
```

This fabfile contains the command `prepare_server`, which executes the previous described actions. It receives the parameters `install_game` (that install the counter strike global offensive server), `cringer_branch` which allows to choose the cringer development branch, and `erase` which must set to `yes` if there was already a server installed with the `steam` user in the target host.

## Requirements

To launch the installer you need to install Python 2.7 first on your system. When it's installed you will need to have the `pip` command available. and then install fabric:
```
$ sudo pip install fabric
```

## How to use the installer

Now you can use the `fab` command. Here are several options:

Installing a csgo server (install_bame=yes) on 185.154.160.67 with the required credential  (-H 185.154.160.67  -u electronicastars -p Electronic1212--), in which there is not a previous instance and cloning the cringer develop branch (cringer_branch=develop).

```
$ fab prepare_server:install_game=yes,cringer_branch=develop -H 185.154.160.67 -u electronicastars -p Electronic1212--
```

Or setup the es-gameserver-dev server ( -H es-gameserver-dev) in which already exists a csgo server instance (erase=yes). It is logged in with a pem key already registered on your system.
```
$ fab -H es-gameserver-dev prepare_server:erase=yes
```

If you want to install the csgo server on 185.154.160.67 with the required credential  (-H 185.154.160.67  -u electronicastars -p Electronic1212--), where there is not a previous csgo instance installed. Using the cringer master branch.

```
$ fab -H es-gameserver-dev prepare_server  -H 185.154.160.67 -u electronicastars -p Electronic1212--
```

Remember, the parameters are:

* install_game: for installing CSGO.
* cringer_branch: to choose the branch to clone.
* erase: if you want to remove the steam user.
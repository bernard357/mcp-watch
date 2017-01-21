# Setup MCP Watch with Qualys

On this page you will find instructions to install MCP Watch with Qualys.

![architecture](media/architecture-qualys.png)

Since Qualys is ran as a public cloud service, you need a computer only
to run the `mcp-pump` software itself. This computer should be given access
to public Internet, so that it can interact with the API endpoints.

### Install the software

For this installation you need a computer that can run python programs,
plus some tools to download software from python public repository, and from GitHub.

Pre-requisites:
- [python 2.7 and pip](https://www.python.org/downloads/)
- [git](https://git-scm.com/downloads)
- [Apache Libcloud](https://libcloud.readthedocs.io/en/latest/getting_started.html)

Download the `mcp-pump` code directly from GitHub:

```
$ git clone https://github.com/bernard357/mcp-pump.git
$ cd mcp-pump
$ pip install -r requirements.txt
```

As an overall example, if you use a Ubuntu machine, you could do the following:

```bash
$ sudo apt-get install -y ntp python-pip git apache-libcloud
$ cd /home/ubuntu/
$ git clone https://github.com/bernard357/mcp-pump.git
$ cd mcp-pump
$ sudo pip install -r requirements.txt
```

### Configure the system

All configuration parameters have been centralised in a single file used by `mcp-pump`:

```
$ sudo nano config.py
```

Every module has a separate section, so it should be easy to move around

Check the Qualys section and ensure that the module has been activated.
Also double-check the URL that will be used to interact with the Qualys API endpoint.
For example if you are located in Europe:

```
qualys = {
    'active': True,
    'url': 'https://qualysguard.qualys.eu/',
    'login': '$QUALYS_LOGIN',
    'password': '$QUALYS_PASSWORD',
    }
```

Save changes with `Ctl-O` and exit the editor with `Ctl-X`.

Put MCP credentials in environment variables:

```
$ export MCP_USER='foo.bar'
$ export MCP_PASSWORD='WhatsUpDoc'
```

Put Qualys credentials also in environment variables:

```
$ export QUALYS_LOGIN='who.knows'
$ export QUALYS_PASSWORD='76gjTdc86'
```

For permanent changes you may put these variables in a file
that is loaded automatically by the operating system.

If you are running Ubuntu or Mac OSX you could do:

```
$ nano ~/.bash_profile
```

and type text like the following:

```
# MCP credentials
$ export MCP_USER='foo.bar'
$ export MCP_PASSWORD='WhatsUpDoc'

# Qualys credentials
$ export QUALYS_LOGIN='who.knows'
$ export QUALYS_PASSWORD='76gjTdc86'
```

Save changes with `Ctl-O` and exit the editor with `Ctl-X`.
Then close all terminal windows, and re-open one to ensure that environment variables have been updated.

### Start the pump

```
$ python pump.py
```

![pumping](media/pumping.qualys.png)

### Check scanning reports

Start the Qualys from your preferred web browser, so that you can monitor the scans performed
and their results.

![Qualys dashboard](media/qualys.dashboard.png)

# Frequently asked questions

## About project governance

### Where is this project coming from?

The MCP Watch project is an initiative from European teams of Dimension Data. It is supported by experts in data centres, in cyber-security and of course in cloud orchestration.

### Is this software available to anyone?

Yes. The software and the documentation have been open-sourced from the outset, so that it can be useful to the global community of MCP practioners. The MCP Watch project is based on the [Apache License](https://www.apache.org/licenses/LICENSE-2.0).

### Do you accept contributions to this project?

Yes. There are multiple ways for end-users and for non-developers to [contribute to this project](contributing.md). For example, if you hit an issue, please report it at GitHub. This is where we track issues and report on corrective actions.

And if you know [how to clone a GitHub project](https://help.github.com/articles/cloning-a-repository/), we are happy to consider [pull requests](https://help.github.com/articles/about-pull-requests/) with your modifications. This is the best approach to submit additional reference configuration files, or updates of the documentation, or even evolutions of the python code.

## About project design

### What is needed to run the pump?

The `mcp-watch` piece of software is written in python and relies on the Apache Libcloud for interactions with the API from Dimension Data. Any computer that can run the python interpreter and that can connect to the public Internet is eligible for the MCP Watch. This can be your own workstation for a quick test or for a demo. Or it can be a small computer like a Raspberry Pi. Or any general-purpose computer, really. And, of course, it can be a virtual server running in the cloud.

### What systems are compatible with MCP Watch?

Currently, MCP Watch can interact with InfluxDB, with Qualys, and with local files. Our mid-term objective is that `mcp-watch` can interface with multiple systems. The architecture is open, so that it can be extended quite easily. We are looking for the addition of Elasticsearch, MongoDB, Cisco Spark and of Splunk. If you are interested, or have other ideas, please have a look at the [contributing page](contributing.md).

### Can I check logs from multiple MCP customers?

No you cannot. The Managed Cloud Platform is multi-tenant down to every log record. Each customer has to use his own MCP credentials and, therefore, access only logs for his own organisation. Dimension Data employees use specific MCP environments restricted to developments, demonstrations, temporary integrations or to other internal usage. Generally speaking, you can get assistance from Dimension Data staff to build any analytics or scanning solution, but in the end some personal MCP credentials will be used.

### When a server is rebooted, does this trigger a security scan?

Yes. The main reason for rebooting a server is that some core software has been changed or reconfigured. Therefore the need for another security scan, that can test the new setup, and validate it. MCP Watch enables continuous protection that goes beyond initial setup of a server in the cloud.

### How do this compare to integrated Continuous Delivery?

The infrastructure-as-code pipeline can integrate automated scans. For example, Jenkins can be configured by DevOps teams so that Qualys scans are performed during Continuous Delivery. However, this integrated approach is not adapted to the separation of duties that characterizes strong security. With MCP Watch, security teams only needs a MCP sub-account, and get visibility on changes done to the virtual infrastructure by other teams in the same overall organisation.

## About project deployment

### How to install MCP Watch with InfluxDB and Grafana?

Check [detailed instructions](setup-influxdb-grafana.md) for step-by-step deployment of a running installation.

### How to install MCP Watch with Qualys?

Check [detailed instructions](setup-qualys.md) for step-by-step deployment of a running installation.

### Is it required to know python?

No. The `mcp-watch` software uses a separate configuration files that can be modified at will, and that requires almost
no knowledge of python. Check `config.py` and change parameters based on instructions there.

### How to run the pump interactively?

Use a terminal window, or go to the server over SSH, and launch execution from the command-line:

```bash
$ python pump.py
```

Break the infinite pumping loop if needed with the keystroke `Ctrl-X`.

### How to retrieve data from the past?

Note: do not do this if the database has been populated, else logs would be recorded multiple times.

If you start with an empty database then indicate how much data you would like to retrieve from the past.
For example here is the command that will fetch daily logs for the past quarter:

```bash
$ python pump.py 3m
```

### Will security scans be launched on servers created days ago?

No. The maximum horizon for scanning is 2 minutes. This has been designed as a dynamic response to infrastructure changes. The Qualys console, or other tools, are more adapted to comprehensive scanning campaigns. You can ask security experts from Dimension Data or from NTT Security for any assistance of course.

### How to make the pump more verbose?

Edit `config.py` and activate the debug mode.

```
pump = {
    'debug': True,
    }
```

Then restart the pump and be prepared for a significant flow of data on screen.

### How to check data flow in InfluxDB?

The creation of the database and the push of data is performed automatically by `mcp-watch`. Data records can be checked with teh `influx` client software like this:

```
influx
```

Once you have the prompt of influx you can type following commands:

```
> show databases
> use mcp
> show series
> select * from "Summary usage"
> select * from "Audit log"
> exit
```

If there is no database, no series, or no data in the two series mentioned, then you know for sure that there is something broken between `mcp-watch` and InfluxDB. Have you activated the debug mode and checked messages from it?

### My problem has not been addressed here. Where to find more support?

Please [raise an issue at the GitHub project page](https://github.com/bernard357/mcp-watch/issues) and get support from the project team.

If you are a Dimension Data employee, reach out the Green Force group at Yammer and engage with
other digital practitioners.



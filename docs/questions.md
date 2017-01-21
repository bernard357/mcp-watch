# Frequently asked questions

## About project governance

### Where is this project coming from?

The MCP Watch project is an initiative from European teams of Dimension Data. It is supported by experts in data centres and in cloud architecture.

### Is this software available to anyone?

Yes. The software and the documentation have been open-sourced from the outset, so that it can be useful to the global community of MCP practioners. The MCP Watch project is based on the [Apache License](https://www.apache.org/licenses/LICENSE-2.0).

### Do you accept contributions to this project?

Yes. There are multiple ways for end-users and for non-developers to [contribute to this project](contributing.md). For example, if you hit an issue, please report it at GitHub. This is where we track issues and report on corrective actions.

And if you know [how to clone a GitHub project](https://help.github.com/articles/cloning-a-repository/), we are happy to consider [pull requests](https://help.github.com/articles/about-pull-requests/) with your modifications. This is the best approach to submit additional reference configuration files, or updates of the documentation, or even evolutions of the python code.

## About project design

### What is needed to run the pump?

The `mcp-pump` piece of software is written in python and relies on the Apache Libcloud for interactions with the API from Dimension Data. Any computer that can run the python interpreter and that can connect to the public Internet is eligible for the MCP Watch. This can be your own workstation for a quick test or for a demo. Or it can be a small computer like a Raspberry Pi. Or any general-purpose computer, really. And, of course, it can be a virtual server running in the cloud.

### What are the systems compatible with MCP Watch?

Currently, MCP Watch can interact with following systems:
- store all logs in InfluxDB
- trigger scans of public cloud servers with Qualys
- dump logs in files

Our mid-term objective is that `mcp-pump` can interface with multiple systems. The architecture is open, so that it can be extended quite easily. We are looking for the addition of Elasticsearch, MongoDB, Cisco Spark and of Splunk. If you are interested, or have other ideas, please have a look at the [contributing page](contributing.md).

## About project deployment

### How to install MCP Watch with InfluxDB and Grafana?

Check [detailed instructions](setup-influxdb-grafana.md) for step-by-step deployment of a running installation.

### How to install MCP Watch with Qualys?

Check [detailed instructions](setup-qualys.md) for step-by-step deployment of a running installation.

### Is it required to know python?

The `mcp-pump` software uses a separate configuration files that can be modified at will, and that requires almost
no knowledge of python. Check `config.py` and change parameters based on instructions there.

### How to run the pump interactively?

Go to the server over SSH, and launch the server from the command-line:

```bash
$ python pump.py
```

### How to make the pump more verbose?

Edit `config.py` and activate the debug mode.

```
pump = {
    'debug': True,
    }
```

Then restart the pump and be prepared for a significant flow of data on screen.

### My problem has not been addressed here. Where to find more support?

Please [raise an issue at the GitHub project page](https://github.com/bernard357/mcp-pump/issues) and get support from the project team.

If you are a Dimension Data employee, reach out the Green Force group at Yammer and engage with
other digital practitioners.



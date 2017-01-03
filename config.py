
#
# General pump settings
#

pump = {

    # regions to be analysed
    #
    'regions': ['dd-af', 'dd-ap', 'dd-au', 'dd-eu', 'dd-na'],

    # should better be set in computer environment
    #
    # 'MCP_USER': 'foo.bar',

    # should better be set in computer environment
    #
    # 'MCP_PASSWORD': 'WhatsUpDoc',

    }

#
# file settings -- uncomment and edit to save on local files
#

files = {
    'summary_usage': './summary_usage.log',
    'detailed_usage': './detailed_usage.log',
    'audit_log': './audit_log.log',
    }

#
# InfluxDB settings -- uncomment and edit if you have an influxdb server
#

#influxdb = {
#    'host': 'localhost',
#    'port': 8086,
#    'user': 'root',
#    'password': 'root',
#    'database': 'mcp',
#    }


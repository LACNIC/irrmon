### Implementation details

------

#### Whois queries

Whois queries are made on the IRR source of the object and on a list of selected mirrors where the existence of said object can be verified. These queries can return the following statuses:

| Resultado                     | Letra | Valor |
| ----------------------------- | ----- | ----- |
| Object Not Found              | D     | 0     |
| Object Found                  | A     | 1     |
| Mirror Response with Nothing  | N     | 2     |
| Mirror TimeOut                | T     | 3     |
| Object Found with Differences | F     | 4     |

#### Directories and volumes

The application has the following directory and file structure within the ***data*** directory that is the base of the application:

```
data
├── html
│   ├── index.php -> irrmon.php
│   ├── input
│   │   ├── irr_input.json
│   │   └── irr_whois_list.json
│   ├── irrmn.php
│   ├── log
│   │   ├── irr_check.log
│   │   └── irr_metrics.json
│   └── objects
│       ├── ALTDB.json
│       ├── LACNIC.json
│       ├── LEVEL3.json
│       ├── NESTEGG.json
│       ├── NTTCOM.json
│       ├── NTT.json
│       ├── PANIX.json
│       ├── RADB.json
│       ├── REACH.json
│       ├── RIPE.json
│       ├── ROGERS.json
│       └── TC.json
└── prometheus
    └── prometheus.yml
```

The ***html*** directory is a volume for the ***lighttpd*** container and is the root directory of the web service where the form to be filled in with query parameters is accessed. It also contains the ***log*** and ***objects*** directories for quick access by web page without needing to enter the container.

In the ***input*** directory, the parameters filled in the form in json format are stored in the file ***irr_input.json***. The ***irr_whois_list.json*** file contains the data that defines each RIR and mirror. This list was obtained from https://www.irr.net/docs/list.html

For example, the ***irr_input.json*** file might contain:

```
{"querySourceIRR":"LACNIC","queryObjectType":"aut-num","queryObject":"AS64136", "queryInterval":"300","queryTimeout":"10","queryMirrorsList":["NTT","RADB","LEVEL3","ROGERS","ALTDB","AOLTW","EPOCH","NESTEGG","PANIX","REACH","TC"]}
```

In the directory ***log*** they are stored in:

***irr_check.log*** Is the application execution log with the queries made to each mirror

***irr_metricss.lo***g The results obtained in each query period in json format. For example:

```
{
    "timestamp": 1667518413,
    "date": "2022/11/03 23:33:33",
    "querySourceIRR": "LACNIC",
    "queryObjectType": "aut-num",
    "queryObject": "AS64136",
    "irr": {
        "ALTDB": "D",
        "AOLTW": "N",
        "EPOCH": "T",
        "LACNIC": "A",
        "LEVEL3": "A",
        "NESTEGG": "D",
        "NTT": "A",
        "RADB": "A",
        "REACH": "D",
        "ROGERS": "A",
        "TC": "D"
    }
}
```

The ***objects*** directory stores the responses to the queries in json format and is used to compare the responses obtained if the objects were found on the mirror.

Finally the directory ***data/prometheus*** is a volume for the container ***prometheus*** and contains the configuration file to connect and periodically fetch the information from the exporter.

#### Docker

To enter each of the containers, you must execute:

```
docker exec -it <contenedor> /bin/bash 
```

Note that if the container does not include bash, use sh:

```
docker exec -it <contenedor> /bin/sh
```

The names of the containers that are running and associated with composer can be obtained by running:

```
docker ps
CONTAINER ID   IMAGE             COMMAND                  CREATED        STATUS        PORTS                                       NAMES
f53668fbbd69   irrmon_app        "python3 ./irrmon.py"    21 hours ago   Up 21 hours   0.0.0.0:8000->8000/tcp, :::8000->8000/tcp   irrmon_app_1
de0219cf08b3   irrmon_lighttpd   "/usr/sbin/lighttpd …"   21 hours ago   Up 21 hours   0.0.0.0:80->80/tcp, :::80->80/tcp           irrmon_lighttpd_1
0a41b420fddb   grafana/grafana   "/run.sh"                21 hours ago   Up 21 hours   0.0.0.0:3000->3000/tcp, :::3000->3000/tcp   irrmon_grafana_1
5735229a0080   prom/prometheus   "/bin/prometheus --c…"   21 hours ago   Up 21 hours   0.0.0.0:9090->9090/tcp, :::9090->9090/tcp   irrmon_prometheus_1
```


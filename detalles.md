### Detalles de la implementación

------

#### Consultas whois

Las consultas whois se realizan sobre el IRR fuente del objeto y sobre un listado de mirrors seleccionados donde constatar la existencia de dicho objeto. Estas consultas pueden devolver los siguientes estados:

| Resultado                     | Letra | Valor |
| ----------------------------- | ----- | ----- |
| Object Not Found              | D     | 0     |
| Object Found                  | A     | 1     |
| Mirror Response with Nothing  | N     | 2     |
| Mirror TimeOut                | T     | 3     |
| Object Found with Differences | F     | 4     |

#### Directorios y volumenes

La aplicación presenta la siguiente estructura de directorios y archivos dentro del directorio ***data*** que es la base de la aplicación:  

```
data
├── html
│   ├── index.php -> irrom.php
│   ├── input
│   │   ├── irr_input.json
│   │   └── irr_whois_list.json
│   ├── irrom.php
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

El directorio ***html*** es un volumen para el contenedor ***lighttpd*** y es el directorio raíz del servicio web donde se accede al formulario a completar con los parámetros de las consultas. También contiene los directorios ***log*** y ***objects*** para un acceso rápido por página web sin necesidad de entrar al contenedor. 

En el directorio ***input*** se almacenan en el archivo ***irr_input.json*** los parámetros completados en el formulario en formato json. El archivo ***irr_whois_list.json*** contiene los datos que definen cada RIR y mirror. Esta lista fue obtenida de https://www.irr.net/docs/list.html

Por ejemplo, el archivo ***irr_input.json*** puede contener:

```
{"querySourceIRR":"LACNIC","queryObjectType":"aut-num","queryObject":"AS64136", "queryInterval":"300","queryTimeout":"10","queryMirrorsList":["NTT","RADB","LEVEL3","ROGERS","ALTDB","AOLTW","EPOCH","NESTEGG","PANIX","REACH","TC"]}
```

En el directorio ***log*** se almacenan en:

***irr_check.log***	Es el log de la ejecución de la aplicación con las consultas realizadas a cada mirror

***irr_metricss.lo***g	Los resultados obtenidos en cada período de consulta en formato json. Por ejemplo:

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

En el directorio ***objects*** se almacenan las respuestas a las consultas en formato json y es usado para comparar las respuestas obtenidas si los objetos fueron encontrados en el mirror.  

Por último el directorio ***data/prometheus*** es un volumen para el contenedor ***prometheus*** y contiene el archivo de configuración para conectarse y traer periódicamente la información del exportador. 

#### Docker

Para ingresar a cada uno de los contenedores se debe ejecutar:

```
docker exec -it <contenedor> /bin/bash 
```

 Tener en cuenta que si el contenedor no incluye bash, usar sh

```
docker exec -it <contenedor> /bin/sh
```

Los nombres de los contenedores que se encuentran corriendo y asociados al composer se pueden obtener ejecutando:

```
docker ps
CONTAINER ID   IMAGE             COMMAND                  CREATED        STATUS        PORTS                                       NAMES
f53668fbbd69   irrmon_app        "python3 ./irrmon.py"    21 hours ago   Up 21 hours   0.0.0.0:8000->8000/tcp, :::8000->8000/tcp   irrmon_app_1
de0219cf08b3   irrmon_lighttpd   "/usr/sbin/lighttpd …"   21 hours ago   Up 21 hours   0.0.0.0:80->80/tcp, :::80->80/tcp           irrmon_lighttpd_1
0a41b420fddb   grafana/grafana   "/run.sh"                21 hours ago   Up 21 hours   0.0.0.0:3000->3000/tcp, :::3000->3000/tcp   irrmon_grafana_1
5735229a0080   prom/prometheus   "/bin/prometheus --c…"   21 hours ago   Up 21 hours   0.0.0.0:9090->9090/tcp, :::9090->9090/tcp   irrmon_prometheus_1
```


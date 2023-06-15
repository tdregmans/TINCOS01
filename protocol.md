# TINCOS01
Connected Systems

Team members:
- Hidde-Jan Daniëls
- Bartholomeus Petrus
- Thijs Dregmans

Last edited on 2023-06-16

## Protocol
In dit bestand spreken we het protocol af waarmee de robots en hun Digital Twins in Webots communiceren.

### Specificaties

#### Semantic
De volgende dingen moeten gecommuniceerd worden:

- De Digital Twin vertelt de server zijn locatie, op de x en y as.
- De Digital Twin vertelt de server de veranderende obstakels, met x en y coördinaten*.
- De server vertelt de Digital Twin de richting waarin hij moet bewegen.
- De server vertelt de Digital Twin welke LED aan moet gaan.
- De server vertelt de fysieke bot welke LED aan moet gaan.
- Het dashboard leest de berichten van de robot naar de server, en noteert de robot.
- Het dashboard vertelt de server waar alle bots uiteindelijk terecht moeten komen.
- Het dashboard roept een nood toestand uit.
- De fysieke robot roept een nood toestand uit.

- Obstakels hoeven maar 1x gecommuniceerd te wordn. 
* Obstakels zijn altijd 1 bij 1.

#### Implementation

Request from bot to server:

```json
{
    "data": 
    {
        "sender": "bot1",
        "target": "server",
        "emergency": 0,
        "msg":
        {
            "currentLocation":
            {
                "x": 0.1,
                "y": -0.3
            },
            "obstacles":
            {
                {
                    "x": 0.1,
                    "y": 0.1,
                },
                {
                    "x": 0.2,
                    "y": -0.3,
                }
            },
        }
    },
    "protocolVersion": 4.1
}
```

Respons from server to bot:

```json
{
    "data": 
    {
        "sender": "server",
        "target": "bot2",
        "emergency": 0,
        "msg":
        {
            "direction": "N" | "E" | "S" | "W" | "",
            "LED": "N" | "E" | "S" | "W" | ""
        }
    },
    "protocolVersion": 4.1
}
```

Instructions for server from dashbaord:

```json
{
    "data": 
    {
        "sender": "dashboard",
        "target": "server",
        "emergency": 0,
        "msg":
        {
            "targetFields":
                {
                    "bot1":
                    {
                        "x": 0.1,
                        "y": 0.1,
                    },
                    "bot2":
                    {
                        "x": 0.4,
                        "y": -0.2,
                    },
                }
        }
    },
    "protocolVersion": 4.1
}
```

what bots are available, is known by the dashboard, as the same way as for the server: bots publish a message with their location.
An emergency from the dashboard, looks the same as for the fysical bots. See here.

Emergency:

```json
{
    "data": 
    {
        "sender": "bot1",
        "emergency": 1
    },
    "protocolVersion": 4.1
}
```
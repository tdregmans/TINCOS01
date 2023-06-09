# Practicum 2
Bartholomeus Petrus
Hidde-Jan Daniëls
Thijs Dregmans
2023-06-09
In dit readme bestand spreken we het protocol af waarmee de robots en hun Digital Twins in Webots communiceren.

### Specificaties

#### Semantic
De volgende dingen moeten gecommuniceerd worden:

- De robot vertelt de server zijn locatie, op de x en y as.
- De robot vertelt de server de veranderende obstakels, met x en y coördinaten*.
- De robot vertelt de server zijn geplande verplaatsing, met de doel coördinaten.

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
    "protocolVersion": 2.0
}
```

Respons from server to bot:

```json
{
    "data": 
    {
        "sender": "server",
        "target": "bot2",
        "msg":
        {
            "targetLocation":
            {
                "x": 0.0,
                "y": -0.2
            }
        }
    },
    "protocolVersion": 2.0
}
```


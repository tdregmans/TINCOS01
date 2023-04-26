# Practicum 2
Bartholomeus Petrus
Hidde-Jan Daniëls
Thijs Dregmans
2023-04-19
In dit readme bestand spreken we het protocol af waarmee de robots en hun Digital Twins in Webots communiceren.

### Specificaties

#### Semantic
De volgende dingen moeten gecommuniceerd worden:

- De robot vertelt de server zijn locatie, op de x en y as.
- De robot vertelt de server de veranderende obstakels, met x en y coördinaten*.
- De robot vertelt de server zijn geplande verplaatsing, met de doel coördinaten.

- Obstakels hoeven maar 1x gecommuniceerd te wordn. 
* Obstakels zijn altijd 1 bij 1.

#### Syntaxis
We kiezen voor de volgende syntax:
```
<msg id>
    528e0649
<msg id>
<data>
    <timestamp>
        1681903388
    <timestamp>
    <sender>
        robot 01
    <sender>
    <target>
        server
    <target>
    <msg>
        <type>
            0
        <type>
        <current location>
            <x>
                0.1
            <x>
            <y>
                -0.3
            <y>
        <current location>
        <target location>
            <x>
                0.0
            <x>
            <y>
                -0.2
            <y>
        <target location>
        <obstacles>
            [
                <obstacle>
                    <x>
                        0.1
                    <x>
                    <y>
                        0.1
                    <y>
                <obstacle>
                <obstacle>
                    <x>
                        0.2
                    <x>
                    <y>
                        -0.3
                    <y>
                <obstacle>
            ]
        <obstacles>
    <msg>
    <protocol version>
        1.0
    <protocol version>
<data>
```
#### Implementation

```json
{
    "msgId": "528e0649",
    "data": 
    {
        "timestamp": 1681903388,
        "sender": "rbt1",
        "target": "server",
        "msg":
        {
            "type": 0,
            "currentLocation":
            {
                "x": 0.1,
                "y": -0.3
            },
            "targetLocation":
            {
                "x": 0.0,
                "y": -0.2
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
    "protocolVersion": 1.0
}
```


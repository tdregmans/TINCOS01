# TINCOS01
Connected Systems

Team members:
- Hidde-Jan Daniëls
- Bartholomeus Petrus
- Thijs Dregmans

Last edited on 2023-06-07

## Opdracht

De opdracht bestaat uit 3 delen:
- De server, gecodeerd in Python
- De clients, gecodeerd in Python/cpp
- Het dashboard, gecodeerd in html/javascript

![Diagram](diagram.png "Diagram van opdracht")

### Server

De server gebruikt MQTT om te communiceren met de clients.

### Client

Er zijn 2 soorten clients:

#### Bot

Een bot is een fysieke ESP32 met cpp code. Het communiceert middels MQTT met de server.
Het heeft 4 LED's om de richtingen aan te geven en een stopknop, om alles te laten stoppen.

#### Digital Twin

Een digital twin van de Bot, gemaakt in WeBots. Hiervoor moet een proto worden ingeleverd. De virtuele bot communiceert met MQTT met de server. De code hiervoor is geschreven in python.

## Beoordeling 
Voor elk van de volgende criteria waaraan volledig is voldaan kan er 1 punt worden verdiend voor het eindcijfer. Alle punten bij elkaar opgeteld vormen het eindcijfer voor het vak Connected Systems.
1. De unit beweegt zich in de gegeven gesimuleerde ruimte.
2. De unit ontwijkt andere aanwezige units en obstakels.
3. De unit wisselt eigen positiegegevens en posities van obstakels uit met de centrale server.
4. De unit bereikt het opgegeven doel.
5. Een display op de unit geeft de gewenste richting aan voor iedere stap.
6. De gewenste richting wordt ook aangeduid op fysieke hardware, en daar is ook een werkende noodstop-knop aanwezig.
7. De routes van de units worden bepaald door middel van een algoritme.
8. Op het dashboard kunnen taken voor de units ingegeven worden en kan een noodstop gegeven worden.
9. Informatie over de positie, de uitgevoerde en de nog openstaande taken van de units wordt afgebeeld op een dashboard.
10. De units verdelen onderling taken afgestemd op de specifieke beperkingen van iedere unit.

Een extra punt kan worden toegekend als de units of het dashboard een extra feature hebben (voorafgaand
aan de toetsing afgestemd met de docent), maar alleen als er aan minstens 6 van bovenstaande criteria
voldaan is.
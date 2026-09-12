# Benchmark work-management en work-triage

Uitgevoerd op 12 september 2026 op verzoek van Sil, vóór het overnemen van de opgeschoonde instructies.

## Resultaat

In 16 synthetische situaties voldeden zowel de oude als de nieuwe instructies aan alle 36 vooraf vastgelegde besliscriteria. Er is binnen deze proef geen gedragsregressie gevonden. De twee hoofdteksten samen zijn 24,3% korter: 2.289 naar 1.732 woorden, inclusief frontmatter.

| Hoofdtekst | Oud | Nieuw | Verschil |
|---|---:|---:|---:|
| work-management | 1.111 | 912 | -17,9% |
| work-triage | 1.178 | 820 | -30,4% |
| Totaal | 2.289 | 1.732 | -24,3% |

De ondersteunende referenties zijn ongewijzigd. Regels over bronhistorie, wachtrijherstel, T3-dispatch en verzendgoedkeuring blijven beschikbaar op dezelfde paden.

## Opzet

- Twee onafhankelijke subagents met dezelfde overgeërfde modelinstellingen en een lege gesprekscontext. Agent A las uitsluitend de oude snapshot; agent B uitsluitend de kandidaat.
- Beiden kregen dezelfde [16 situaties](cases.md) en relevante referenties binnen hun eigen snapshot. Ze mochten geen live accounts, services, andere snapshot of beoordelingscriteria raadplegen.
- De [36 criteria](criteria.json) waren vastgelegd vóór de agents werden gestart. De hoofdagent beoordeelde de antwoorden achteraf handmatig. De beoordelaar wist welke versie oud en nieuw was.
- De agents leverden voorgestelde beslissingen. Er zijn geen Notion-, Gmail-, Slack-, Calendar- of T3-operaties uitgevoerd en geen collectorscripts gestart.
- De [antwoorden van A](responses-a.md) en [antwoorden van B](responses-b.md) zijn ongewijzigd bewaard. Er was geen tweede ronde of aanpassing van de kandidaat na het bekijken van de antwoorden.
- De fixture-identiteiten zijn synthetisch. Waar een native URL of exacte datum niet letterlijk in de fixture stond, moesten de agents die onzekerheid behouden in plaats van gegevens te verzinnen.

## Beoordeling

Een criterium telt als voldaan wanneer het antwoord alle daarin genoemde beslisvoorwaarden respecteert. Verschillen in formulering of extra operationele toelichting zijn niet als verschil in gedrag geteld.

| Situatie | Onderwerp | Oud | Nieuw |
|---|---|---:|---:|
| 01 | Al beantwoorde klantvraag | 2/2 | 2/2 |
| 02 | Ontbrekende bestanden en contactgegevens | 3/3 | 3/3 |
| 03 | monday-tickets en gedeeltelijke blokkade | 2/2 | 2/2 |
| 04 | Gelijkende namen, andere klant | 2/2 | 2/2 |
| 05 | Nieuw werk naast afgeronde taak | 2/2 | 2/2 |
| 06 | Annuleren en planningsvelden leegmaken | 2/2 | 2/2 |
| 07 | Voorstel is geen afspraak | 2/2 | 2/2 |
| 08 | Menselijke conceptbewerkingen behouden | 2/2 | 2/2 |
| 09 | Onleesbare bron en onafhankelijk werk | 2/2 | 2/2 |
| 10 | Feedback naar open, gesnoozede T3-thread | 2/2 | 2/2 |
| 11 | Afgeronde thread en onbevestigd extra werk | 2/2 | 2/2 |
| 12 | Goedkeuring voor verouderde berichttekst | 2/2 | 2/2 |
| 13 | Ontbrekend ontvangstbewijs en onvolledige bron | 3/3 | 3/3 |
| 14 | Offerteacceptatie en overdracht naar delivery | 3/3 | 3/3 |
| 15 | Correctie zonder bronhistorie te overschrijven | 2/2 | 2/2 |
| 16 | Kalenderwijziging en terugkerende bronfout | 3/3 | 3/3 |
| **Totaal** | | **36/36** | **36/36** |

Beide agents behielden menselijke conceptbewerkingen, maakten geen dubbele taken of threads, verzonnen geen akkoord of datum, hielden onbekende bijlagen open en behandelden een oude goedkeuring niet als toestemming voor gewijzigde tekst. Ze lieten succesvolle onafhankelijke verwerking doorgaan wanneer een andere bron ontbrak. Een gesnoozede open thread mocht kwalificerende feedback krijgen; een afgeronde thread werd niet automatisch heropend.

## Grenzen

Dit is een beperkte beslisbenchmark met één run per versie, geen statistisch bewijs of live integratietest. De bronfeiten en verificatieresultaten zijn vooraf aangeleverd; het vermogen om die feiten zelfstandig uit echte systemen te verzamelen is niet getest. Looptijd, API-betrouwbaarheid, modeltokenverbruik en andere modellen zijn niet vergeleken. De woordreductie geldt voor de hoofdteksten, niet voor alle mogelijk geladen referenties.

De resultaten ondersteunen het overnemen van deze tekstuele opschoning. De bestaande scripts en externe automatiseringsinstellingen blijven ongewijzigd.

## Reproduceerbaarheid

De oude hoofdteksten komen uit commit `5a27319` van `fulldotdev/agents`. De onderstaande SHA-256-waarden identificeren de daadwerkelijk beoordeelde bestanden.

| Variant | Bestand | SHA-256 |
|---|---|---|
| A | work-management/SKILL.md | `a8554af7c12995ea684165871fa83a6b6893b8d8909611b3553d13b09ea9aae7` |
| A | work-triage/SKILL.md | `37f0a24640c7f8b83462787b56e3cc49378cb5f9dcdc39e74eaa6b6ca36c430e` |
| B | work-management/SKILL.md | `8a2259e63aadf6f947a69bb32a4e35f76b64144b0cd5cbf04191f28c9801aec0` |
| B | work-triage/SKILL.md | `a2dcdbaae5ebb8f774d9546dcdfe5990dcbe9407ee6e80f98d38eb7423b7eb7e` |

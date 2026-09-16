---
name: target-relationships
description: Onderzoek relevante mensen en contactaanleidingen rond Sil's targetbedrijven. Maak een dagelijkse netwerklijst, met een kort conceptbericht wanneer daar een concrete aanleiding voor is. Sil voert het contact zelf uit.
---

# Netwerk rond targetbedrijven

Help Sil relevante mensen te leren kennen bij bedrijven waarmee FullDev zou kunnen samenwerken. Nieuwe mensen vinden staat voorop; recente posts, events en gedeelde relaties kunnen een natuurlijke aanleiding geven voor contact.

## Start

Draai eerst het verzamelscript en lees het bestand dat het noemt:

```bash
python3 ~/.agents/skills/target-relationships/scripts/collect.py
```

Het bevat de Companies met Status `Target` uit Notion met hun notities en website, de mensen die al in Dex bij die bedrijven staan, wie de laatste drie weken al in een lijst stond, en Sils DM-voorbeelden. Lees daarna de laatste berichten van Sil in de Telegram Sales-chat (session `agent:main:telegram:group:-5101802924`) voor feedback op eerdere lijsten. Zoek niets van dit alles zelf opnieuw op; de rest van het werk is LinkedIn- en webonderzoek.

## Selectie en context

- De targetbedrijven en hun notities bepalen de doelgroep en mogelijke samenwerking; houd geen tweede bedrijvenlijst in deze skill of de automatiseringsprompt bij.
- Bureaus moeten aantoonbaar website- of webshopprojecten oppakken, via ontwerp of realisatie; alleen branding, flyers of packaging is onvoldoende. Eigen developers in-house zijn geen harde eis.
- Kies mensen die betrokken zijn bij klanten, partnerships, ontwerp, marketing, commerce of development. Beoordeel wat FullDev kan aanvullen. Een vergelijkbare technische stack of een groeiend bureau bewijst geen behoefte aan uitbesteding; neem eigen developmentcapaciteit en tijdzone mee wanneer die de samenwerking beïnvloeden.
- Iemand buiten een targetbedrijf past alleen bij een aantoonbare verbinding, zoals samenwerking of een relevante eerdere rol. Benoem die verbinding; dezelfde branche of alleen een gezamenlijke LinkedIn-connectie is onvoldoende.
- Gebruik de Dex-contacten, de Sales-chat en de lijst met eerdere suggesties uit het verzamelbestand om relaties, verstuurde verzoeken en eerdere suggesties te herkennen. Dex-aanwezigheid, een verzonden verzoek en een geaccepteerde connectie zijn verschillende feiten. Een eerdere suggestie bewijst geen contact.
- Verifieer de huidige rol, het profiel en de aanleiding. Bekijk relevante persoonlijke posts, bij voorkeur uit de afgelopen week. Spreid het onderzoek over targetbedrijven en herhaal een persoon alleen bij een nieuwe aanleiding.

## Contactaanleiding

Een inhoudelijke post, event of bevestigd gedeeld partnerschap kan een korte contactsuggestie verdienen. Voeg alleen dan een menselijk conceptbericht toe, in de taal van de ontvanger. Gebruik Sils DM-voorbeelden uit het verzamelbestand als stijlhouvast, niet als template: kort, oprecht en concreet, zonder verplichte pitch of afsluitende vraag, en zonder typefouten of onbewezen aanleidingen uit de voorbeelden over te nemen. Is de pagina niet leesbaar, meld dat kort en laat conceptberichten weg. Gebruik `customer-communication` voor de formulering. Benoem de concrete aanleiding zonder een bestaande relatie, bekendheid of behoefte te suggereren die niet is vastgesteld. Geen algemene salespitch of verplicht bericht bij ieder item. Herhaal dezelfde kennismakingsaanleiding niet zonder nieuwe context.

Dit blijft onderzoek en voorbereiding: wijzig geen Notion- of Dex-records en verstuur geen connectieverzoeken, berichten, reacties of likes. Sil kiest en voert het contact uit. Gebruik voor browserwerk Chrome volgens de globale browserregels. Sluit eigen onderzoekstabs na afloop en behoud bestaande tabs.

## Dagelijkse lijst

Geef een compacte, genummerde lijst in het Nederlands met tien goed onderbouwde items. Zoek bij meerdere targetbedrijven; geef minder als er onvoldoende verifieerbare vondsten zijn en benoem kort wat ontbreekt.

Zet nieuwe mensen vooraan. Geef per item de naam met directe LinkedIn-profiellink, huidige rol, bedrijf en concrete relevantie. Link een aangehaalde post rechtstreeks en noem de datum. Maak bij een persoon buiten het targetbedrijf de verbinding duidelijk. Een passende contactsuggestie en eventueel conceptbericht staan direct onder het bijbehorende item.

Verifieer de links en markeer onbekende connectiestatus als onbekend. Laat een algemene inleiding en afsluiting weg. Zonder bruikbare vondsten: `Vandaag geen nieuwe, goed onderbouwde ingangen gevonden.`

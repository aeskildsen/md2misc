

# Dine næste skridt



Tillykke med, at du har læst denne bog og forhåbentlig har arbejdet aktivt med dens indhold på egen hånd. Du har i så fald gennemført et stort stykke arbejde, som jeg håber har været udbytte- og lærerigt. Men din rejse udi komposition og lydproduktion med SuperCollider behøver ikke slutte her. Herunder deler jeg et par ideer til hvad du kan arbejde videre med efter denne bog, samt hvilke andre læringsmaterialer, du med fordel kan opsøge. God fornøjelse med din videre færd udi (computer)musikkens forunderlige verden.

## Ideer til projekter og kompositioner



Når du har fået styr på det grundlæggende, åbner der sig et væld af muligheder. Her er nogle ideer til, hvordan du kan arbejde videre med komposition og lydproduktion i SuperCollider, både i forhold til tekniske og kunstneriske projekter.

### Kompositionsideer



Opstil dogmer og benspænd

:   Sæt kreative benspænd for dig selv, fx at din kompositionen højst må vare ét minut og kun må bruge `SinOsc`, `Env.sine` og `Pseries`. Eller at et helt værk skal genereres ud fra [tekststrenge fra dit yndlingsdigt, der omsættes til tonehøjder og rytmer](../02/e-generativ-komposition.md#sekvens-og-generativitet). Eller at du fremstiller en komposition udelukkende i én UGen-funktion, hvor formen bestemmes af en eller flere envelopes og LFO'er.

Fortolk et eksisterende værk

:   Prøv at implementere et kendt værk i SuperCollider, ligesom [vi arbejdede med en del af Steve Reichs *Piano Phase*](../03/a-sammensaetning.md#en-minimalistisk-kompositionside). Det kræver, at du oversætter og fortolker værkets instrukser til kildekode, hvilket både kan være en kreativ og lærerig proces. Du kan derefter skrive din egen komposition, inspireret af din indsigt i det andet værk.

Kombinér SuperCollider med andre teknologier

:   Der er ingen grund til at at være SuperCollider-purist og udføre alt sit lydarbejde med ét redskab. Ofte kan det være inspirerende at kombinere forskellige teknologier og se, hvad den særlige kombination lægger op til. Brug fx SuperCollider som MIDI-generator til dit yndlings-plugin i en DAW. Eller indlæs VST plugins i SuperCollider med udvidelsen [VSTPlugin](https://git.iem.at/pd/vstplugin) og komponér løs med patterns og UGens.

Udforsk klangdannelsesteknikker

:   Dyk ned i teknikker som FM/PM-syntese, granular-syntese, physical modelling osv. Brug litteratur om disse teknikker som inspiration (se hertil litteraturhenvisningerne i denne bog), og prøv at implementere teknikkerne i SuperCollider. Brug patterns til at udforske mulighederne i de SynthDefs, du kan konstruere. Det er både lærerigt og giver masser af nye ideer til egne kompositioner.

### Projektideer



Skab dit eget unikke sample-bibliotek

:   Lav dine egne samlinger af beats, lydeffekter, trommelyde, abstrakte lydtæpper, køkkenlyde eller hvad du nu kan finde på – alt sammen genereret eller manipuleret i SuperCollider. Husk, at SuperCollider også er et programmeringsredskab. Du kan derfor beskrive algoritmer, som genererer et væld af variationsmuligheder, som du kan modificere og selektere i.

Byg din egen synthesizer

:   Design og programmér din egen synthesizer, evt. med et MIDI-keyboard som input. Prøv at køre det hele på en minicomputer som [Raspberry Pi](https://github.com/supercollider/supercollider/blob/develop/README_RASPBERRY_PI.md) for at gøre det til et selvstændigt instrument. Konsultér Marije Baalmans glimrende bog om udvikling af sådanne interaktive systemer [@baalman2022], og se evt. Eli Fieldsteels guide til organisering af større SuperCollider-projekter [@fieldsteel2024a, p. 249].

GUI (graphical user interface)

:   Skab dine egne grafiske brugerflader i SuperCollider og brug dem til at styre en algoritmisk komposition. Start med Eli Fieldsteels [tutorial om GUI](https://www.youtube.com/watch?v=W2D_PzOVfT0) [@fieldsteel2015].

Udforsk nye klange med wavetables

:   Dette emne kan du let sætte dig ind, da det beror på en grundlæggende forståelse af buffere og oscillatorer. Med wavetables kan man i princippet spille med enhver bølgeform, og der findes ganske mange gratis wavetables, fx pakken [AKWF FREE](https://www.adventurekid.se/akrt/waveforms/adventure-kid-waveforms/), som allerede er [konverteret til SuperColliders wavetable-format](https://github.com/terrymullett/AKWF-SuperCollider).

Udforsk udvidelser til SuperCollider

:   Prøv kræfter med de mange udvidelser, der findes til SuperCollider, og se, hvordan de kan udvide dine muligheder. Start med at kigge på de mange forskellige [Quarks](https://github.com/supercollider-quarks/quarks) og [ekstra plugins](https://supercollider.github.io/sc3-plugins/). Kig også på den desværre ikke helt opdaterede men alligevel velkuraterede liste [Awesome SuperCollider](https://github.com/madskjeldgaard/awesome-supercollider).

Deltag i open source-fællesskabet

:   Engagér dig i online-fællesskaber som [scsynth.org](https://scsynth.org/), studér andres ideer på [sccode.org](http://sccode.org/) og følg med på sociale medier. Her kan du finde inspiration, få hjælp og dele dine egne projekter. Denne bog handler om open source software, og hermed er opfordringen givet videre til at udbrede open source-kulturen yderligere - til alles fordel.

## Ressourcer til videre studier



Selvom denne bog har givet dig en grundig introduktion til komposition og lydproduktion i SuperCollider, kan én tekst dog ikke gøre rede for alt. Der findes heldigvis glimrende læringsmaterialer om anvendelse af SuperCollider, som dog stort set alle er på engelsk. Men det er altid lærerigt og bestemt indsatsen værd at genstudere det samme emne gennem andre forfattere og underviseres perspektiv. Dette skyldes blandt andet, at programmering ofte - og i SuperCollider i særdeles - kan udføres på mange forskellige måder. Med afsæt i denne bog har du gode forudsætninger for at forstå den tekniske lingo, som måske i første omgang kan virke afskrækkende, når man dykker ned i litteraturen. Følgende ressourcer med fokus på SuperCollider henvender sig både til begyndere og til de, som har styr på det grundlæggende og er interesseret i mere avancerede teknikker. De får alle en klar anbefaling herfra, og med afsæt i denne bog kan de nedenstående ressourcer hjælpe dig langt videre.

### Anbefalede materialer til begyndere



- E-bogen [*A Gentle Introduction to SuperCollider*](https://ccrma.stanford.edu/~ruviaro/texts/A_Gentle_Introduction_To_SuperCollider.pdf) af Bruno Ruviaro [-@ruviaro2015] er en glimrende, og som titlen indikerer, blid introduktion til SuperCollider. Den kan ikke anbefales nok.
- Videoserien [*SuperCollider Tutorials*](https://www.youtube.com/playlist?list=PLPYzvS8A_rTaNDweXe6PX4CXSGq4iEWYC) af Eli Fieldsteel [-@fieldsteel2024] er ganske enkelt fremragende, ikke blot som formidling af grundlæggende programmering i SuperCollider, men (især i den sidste halvdel af serien) også som en god introduktion til kerneemner inden for computermusikken. Serien har udgjort en af de primære ressourcer i mine egne studier udi SuperCollider.
- Bogen [*SuperCollider for the Creative Musician: A Practical Guide*](https://academic.oup.com/book/55790), også af Eli Fieldsteel [-@fieldsteel2024a], er en rigtig god introduktion til SuperCollider for musikere.

### Anbefalede materialer på videregående niveau



- E-bogen [*Scoring Sound: Creative Music Coding with SuperCollider*](https://leanpub.com/ScoringSound) af Thor Magnusson [-@magnusson2021] er en meget grundig og omfangsrig introduktion til ikke blot SuperCollider men også kerneemner som klangdannelse og elektronisk komposition inden for computermusik. Den har været et lærerigt bekendtskab i min egen rejse med SuperCollider.
- Bogen [*Introduction to SuperCollider*](https://www.logos-verlag.de/cgi-bin/engbuchmid?isbn=4017&lng=eng&id=) er en engelsk oversættelse af Andrea Valles [-@valle2016] udmærkede grundbog om SuperCollider.
- Videoserien [*Musical Sound Design In SuperCollider*](https://www.youtube.com/playlist?list=PLXCUkMwOEWQtB-leHHSexTizzcACdozp9) af Alik Rustamoff [-@rustamoff2022] introducerer til avancerede emner inden for klangdannelse og lyddesign, med fokus på FM, wavetable-syntese, rumklangsdesign, lofi-æstetik og meget mere.

Der findes mange andre materialer, som kunne have været nævnt her, men jeg har primært nævnt de ressourcer, jeg selv har et godt kendskab til og kan anbefale til denne bogs læsere. God fornøjelse med at udforske dem på egen hånd.

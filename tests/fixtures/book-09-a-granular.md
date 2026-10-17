


Dette kapitel introducerer til granular syntese som teknik og kompositionsredskab i SuperCollider. Vi ser på grundlæggende aspekter som lydkilde, forskellen på synkron og asynkron granular syntese, samt hvordan man automatisk kan udregne centrale parametre som grainvarighed, tæthed og triggerfrekvens. Vi ser også på hvordan man med granular syntese kan at transponere et sample uden ændring i tempo og vice versa, samt hvordan vi med disse redskaber også kan skabe unikke teksturer og klangflader på måder, som ikke er praktisk mulige med traditionelle samplere eller synthesizere.

# Redskaber til granular syntese



Granular syntese er kort fortalt en teknik, der går ud på at danne komplekse klange og teksturer ved at sammensætte korte lydklip ("grains") til unikke strømme af lyd. Grains varer typisk mellem 1 og 100 ms [@roads2002, p. 87], hvilket er meget korte tidsrum at klippe og sammensætte med magnetbånd og andre analoge teknologier. Vi har derfor at gøre med en af de klangdannelsesteknikker, som hører til den digitale lydteknologi. Granular syntese gør arbejdet med lydmateriale utroligt fleksibelt, og SuperCollider indeholder heldigvis glimrende redskaber til at arbejde med teknikken.

På den ene side er granular en metode til at adskille de såkaldte frekvens- og tidsdomæner. Det betyder fx at man kan undgå, at et vokalsample bliver til en musestemme, selvom man sætter tempoet op (eller omvendt). Men på den anden side er granular oplagt til mere abstrakte former for lydproduktion, til at skabe unikke teksturer, klangflader og sågar abstrakte grooves, som ikke kan fremstilles på anden vis. Vi kan med granular syntese strække lyden, så de små detaljer vi ellers ikke bemærker, bliver forstærket og forlænget i det uendelige. Vi kan også sammensætte lyde fra meget forskellige sammenhænge til ét klangtæppe. Her gives en grundlæggende introduktion til disse sider af granular syntese, idet mere teknisk interesserede læsere henvises til Curtis Roads' uomgængelige grundbog om emnet, *Microsound* [@roads2002].

## Kildemateriale



Man kan i princippet danne grains af hvilken som helst lydkilde. I SuperCollider findes der indbyggede UGens til at arbejde med syntetisk dannede grains (`GrainSin` og `GrainFm`), livelyd (`GrainIn`) og lydmateriale indlæst i en buffer (`GrainBuf` og `TGrains`). Man kan også foretage granular syntese "manuelt", fx med `PlayBuf` eller `BufRd`, jævnfør [forrige kapitel](../08/a-samples.md).

Det nok mest anvendte kildemateriale inden for granular syntese er samples. Når man vælger sit lydmateriale, skal man være klar over, at pauser eller stilhed i kildematerialet også bliver til stilhed, når det bliver afspillet i grain-form. Det er også væsentligt at gøre sig klart, om lydmaterialet primært indeholder tonale lyde (fx sang, akkord- eller blæser-/strygerinstrumenter) eller ikke-tonale lyd som feltoptagelser, støj, percussion osv.

Herunder tager vi udgangspunkt i et sample, der indeholder tonalt materiale i form af nogle toner spillet på en kalimba samt lidt baggrundstøj. `GrainBuf`, som vi primært skal arbejde med, kan kun læse fra én kanal ad gangen. Man kan sagtens modulere/ændre hvilken buffer, der læses fra, men vi kan kun læse fra én ad gangen. Bufferne som indeholder lydmaterialet skal derfor indeholde præcis én kanal (dvs. mono), hvorfor vi herunder kun [indlæser den ene kanal](../08/a-samples.md#indlsning-af-enkeltkanaler-fra-lydfiler).

```sc title="Indlæsning af sample til eksempler på granular syntese"
// Indlæs sample i mono - husk at erstatte stien til en lydfil på din egen computer
~kalimba = Buffer.readChannel(s, "C:/lydfiler/kalimba.wav", channels: [0]);
~kalimba.play;
```

![audio/ogg](../media/audio/09-kalimba.ogg)
![audio/mpeg](../media/audio/09-kalimba.mp3)

Vi kan fremstille et enkelt grain ved at afspille samplet med amplituden styret af en kort envelope. Der findes mange forskellige envelopes, som kan anvendes til grains, hvilket vi overlader til nysgerrige læser at nærstudere i litteraturen på området [@roads2002, p. 88]. Her anvender vi for illustrationens skyld en sinusbølge-lignende envelope med en varighed på 50 ms sammen med `PlayBuf`, der starter afspilningen en fjerdedel inde i samplet.

```sc title="Afspilning af et enkelt grain"
{
    PlayBuf.ar(1, ~kalimba, startPos: BufFrames.kr(~kalimba) * 0.25)
    * Env.sine(0.050).ar(2)
}.play;
```

![audio/ogg](../media/audio/09-enkelt-grain.ogg)
![audio/mpeg](../media/audio/09-enkelt-grain.mp3)

![Bølgeform for et enkelt grain](../media/figures/09-grain-waveform.png){ width="70%" }

![Envelope for et enkelt grain](../media/figures/09-grain-envelope.png){ width="70%" }

Selvom vi fint kunne fremstille grains på denne måde, er det mere oplagt at anvende specialindrettede redskaber som UGen'en `GrainBuf`.

## Granular syntese med GrainBuf



Når vi arbejder med granulering af lydmateriale fra en `Buffer` er det oplagt at anvende `GrainBuf`, som netop læser grains fra en buffer. `GrainBuf.ar` har en række argumenter[^1], som det er mest oplagt at demonstrere herunder. Her hører vi:

- 5 grains pr. sekund,
- hver med en varighed på 25 ms,
- læst fra midten af den buffer, hvor vores sample er indlæst,
- afspillet ved almindelig afspilningshastighed (her er `BufRateScale` *ikke* nødvendig, da `GrainBuf` tager højde for forskelle i samplerate),
- og placeret i midten af et stereofelt.

```sc title="Brug af GrainBuf"
{
    GrainBuf.ar(
        // Antallet af output-kanaler
        numChannels: 2,

        // Et triggersignal, som udløser grains
        trigger: Impulse.ar(5),

        // Varigheden af grains
        dur: 0.025,

        // Den buffer, grains skal læses fra
        // Bufferen skal indeholde én lydkanal (mono)
        sndbuf: ~kalimba,

        // Afspilningshastighed for grains
        rate: 1,

        // Læseposition i bufferen
        // 0 er begyndelsen og 1 er slutningen
        pos: 0.5,

        // Position i stereofelt, ligesom ved Pan2 (når der arbejdes med 2 output-kanaler)
        pan: 0
    );
}.play;
```

![audio/ogg](../media/audio/09-grainbuf-indstillinger.ogg)
![audio/mpeg](../media/audio/09-grainbuf-indstillinger.mp3)

Det lyder ikke af meget endnu, da vi har indstillet `GrainBuf` meget monotont og kedeligt for at demonstrere, hvordan den fungerer. Men det laver vi lige straks om på.

[^1]: Der findes yderligere argumenter til `GrainBuf`, men de er af mindre betydning for den grundlæggende anvendelse. Nysgerrige læsere henvises til [SuperColliders dokumentation](https://doc.sccode.org/Classes/GrainBuf.html).

## Synkron og asynkron granular syntese



Et af argumenterne til `GrainBuf.ar` fortjener særlig uddybning, nemlig triggeren. Den fortæller nemlig `GrainBuf`, hvornår der skal udløses et nyt grain. Når vi vælger trigger, vælger vi samtidig mellem *synkron* og *asynkron granular syntese*.

Synkron granular syntese med `Impulse` som trigger

:   Med `Impulse` som trigger starter vi grains med ensartede tidsintervaller, der styres med den *triggerfrekvens*, vi angiver som første argument (`freq`) til `Impulse.ar`. Dette kaldes *synkron granular syntese* [@roads2002, p. 93].

Asynkron granular syntese med `Dust` som trigger

:   `Dust` genererer triggere med mere uregelmæssige tidsintervaller. Man angiver som første argument (`density`) til `Dust.ar` det ønskede, gennemsnitlige antal triggere pr. sekund, hvilket i vores lyddesign er sammenligneligt med triggerfrekvensen for `Impulse`. Med `Dust` som trigger producerer vi såkaldt *asynkron granular syntese* [@roads2002, p. 96].

![To triggere: Impulse og Dust](../media/figures/triggere.png){ width="80%" }

Vi kan bruge [multichannel expansion](../07/a-oscillatorbanke.md#multikanalslyd-med-multichannel-expansion) til at demonstrere forskellen på `Impulse` (venstre kanal) og `Dust` (højre kanal) som trigger ved en lav triggerfrekvens/tæthed med (omtrent, ved brug af `Dust`) 5 grains pr. sekund.

```sc title="Impulse og Dust som trigger til GrainBuf" hl_lines="4"
{
    GrainBuf.ar(
        numChannels: 1,
        trigger: [Impulse.ar(5), Dust.ar(5)],
        dur: 0.100,
        sndbuf: ~kalimba,
        pos: 0.4
    );
}.play;
```

![audio/ogg](../media/audio/09-trigger-sammenligning.ogg)
![audio/mpeg](../media/audio/09-trigger-sammenligning.mp3)

Men hvorfor bruge den ene frem for den anden tilgang her? Man kan selvfølgelig have en æstetisk præference for det mere spredte eller kaotiske udtryk, som kendetegner asynkron granular syntese med `Dust` eller det mere rytmiske udtryk, der kendetegner synkron granular syntese med `Impulse`. Men for at forklare forskellen på de to tilgange er det nyttigt at dvæle ved perceptionen af granular syntese ved forskellige triggefrekvenser.

### Effekter af forskellige triggerfrekvenser



Det er almenkendt, at den laveste tonefrekvens, det menneskelige øre kan opfatte, ligger omkring 20 Hz. Men hvad sker der under 20 Hz, og hvordan opfatter vi granular syntese, når vi bruger en triggerfrekvens, som ligger på over eller under dette skel?

Triggerfrekvenser under 20 Hz

:   Når vi hører grains med hørbart anslag/attack produceret med en (trigger)frekvens på under 20 Hz, hører vi i udgangspunktet lyden som noget rytmisk (ved synkron granular syntese) eller noget arytmisk (ved asynkron granular syntese).

Triggerfrekvenser over 20 Hz

:   Ved højere triggerfrekvenser smelter vores grains sammen i en kontinuerlig strøm. Med synkron granular syntese skaber triggeren sammen med amplitude-envelopen en periodisk amplitude-modulation, hvor triggerfrekvensen træder frem som et hørbart artefakt, ofte med særskilt tonehøjde og hørbare "sidebånd". Den har ofte en lidt "metallisk" klang, som granular syntese i noget omfang er blevet kendt for. For at modvirke dette kan vi bruge asynkron granular syntese, der ikke resulterer i samme periodiske mønster.

Vi kan få en fornemmelse af forskellen ved at skifte mellem forskellige triggerfrekvenser, som ligger under og over 20 Hz. Herunder først den synkrone granular syntese, hvor vi hører en tydelig tonehøjde og "metallisk" klang, når triggerfrekvensen er over 20 Hz.

```sc title="Synkron granular syntese med forskellige triggerfrekvenser" hl_lines="2 5"
{
    var trigFreq = Env.new([1, 2, 5, 10, 15, 25, 50, 100, 200, 300], 1, \step).kr.poll;
    GrainBuf.ar(
        numChannels: 1,
        trigger: Impulse.ar(trigFreq),
        dur: 0.05,
        sndbuf: ~kalimba,
        pos: 0.1
    ) * 0.1;
}.play;
```

![audio/ogg](../media/audio/09-synkron-granular-triggerfrekvens.ogg)
![audio/mpeg](../media/audio/09-synkron-granular-triggerfrekvens.mp3)

Med den asynkrone granular syntese hører vi ikke samme skift i tonehøjde som ovenfor, da tonehøjden i det oprindelige sample bevares.

```sc title="Asynkron granular syntese med forskellige triggerfrekvenser" hl_lines="2 5"
{
    var trigFreq = Env.new([1, 2, 5, 10, 15, 25, 50, 100, 200, 300], 1, \step).kr.poll;
    GrainBuf.ar(
        numChannels: 1,
        trigger: Dust.ar(trigFreq),
        dur: 0.05,
        sndbuf: ~kalimba,
        pos: 0.1
    ) * 0.1;
}.play;
```

![audio/ogg](../media/audio/09-asynkron-granular-triggerfrekvens.ogg)
![audio/mpeg](../media/audio/09-asynkron-granular-triggerfrekvens.mp3)

## Tæthed i strømmen af grains



En central parameter i granular syntese er tætheden mellem grains, dvs. om vi hører én kontinuerlig strøm af grains, eller om vi hører korte lydbidder med "luft" imellem. Tæthed afhænger af forholdet mellem to af de parametre, vi angiver som argumenter til `GrainBuf`: Grainvarighed og triggerfrekvens. Man kan beregne mængden af tæthed med følgende simple formel:

$$
\text{\small tæthed} = \text{\small triggerfrekvens} \times \text{\small grainvarighed}
$$

Som eksempel kan vi tale om forskellige tætheder:

- Ved en triggerfrekvens på 100 Hz og en grainvarighed på 1/100 sekund vil der hverken være overlap eller luft mellem de enkelte grains: $100 Hz \times 1/100 s = 1$
- Var triggerfrekvensen på 50 Hz, ville tætheden være ½, dvs. der vil være stilhed 50% af tiden: $50 Hz \times 1/100 s = 0,5$
- Med en triggerfrekvens på 200 Hz, vil der konstant være 2 samtidigt klingende grains: $200 Hz \times 1/100 s = 2$

Rent kompositorisk er de mest interessante parametre at angive fast eller modulere med LFO'er nok tæthed og grainvarighed. Den konkrete triggerfrekvens kan vi udregne ved at isolere den i ovenstående ligning. Ønsker vi i stedet at angive triggerfrekvensen direkte for at opnå en bestemt effekt, kan vi også gøre det. Ønsker man at angive triggerfrekvens og mængde af tæthed for at lade SuperCollider udregne grainvarigheden, eller lade SuperCollider udregne mængden af tæthed ved specificerede triggerfrekvenser og grainvarigheder, kan man ligeledes isolere den ubekendte i ligningen:

$$
\begin{aligned}
\text{\small tæthed} &= \text{\small triggerfrekvens} \times \text{\small grainvarighed} \\
\iff \text{\small triggerfrekvens} &= \frac{\text{\small tæthed}}{\text{\small grainvarighed}} \\
\iff \text{\small grainvarighed} &= \frac{\text{\small tæthed}}{\text{\small triggerfrekvens}}
\end{aligned}
$$

Hvis fx grainvarighed og tæthed er styret af patterns via SynthDef-argumenter eller af en LFO, kan vi således beregne triggerfrekvensen automatisk. Herunder får vi eksempelvis fornemmelsen af, at lyden "strækkes", fordi der kommer luft i strømmen af grains, når mængden af tæthed, styret af LFO'en `LFTri`, dykker ned under 1.

```sc title="Automatisk beregning af triggerfrekvens" hl_lines="2-4"
{
    var grainDur = 0.050;
    var density = LFTri.kr(0.5).exprange(0.5, 2);
    var trigFreq = (density / grainDur);

    GrainBuf.ar(
        numChannels: 2,
        trigger: Impulse.ar(trigFreq),
        dur: grainDur,
        sndbuf: ~kalimba,
        pos: LFSaw.ar(1/~kalimba.duration, 1).unipolar
    );
}.play;
```

![audio/ogg](../media/audio/09-automatisk-triggerfrekvens.ogg)
![audio/mpeg](../media/audio/09-automatisk-triggerfrekvens.mp3)

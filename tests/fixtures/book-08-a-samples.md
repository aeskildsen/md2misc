


Vi har indtil nu arbejdet med rent syntetisk dannede klange i SuperCollider. Men der er også gode muligheder for at arbejde med præindspillet lyd eller for den sags skyld live-lyd fra en mikrofon eller andet musikudstyr. Her koncentrerer vi os i første omgang om at arbejde med samples i form af præeksisterende lydfiler, som vi først indlæser og derefter kan bearbejde i SuperCollider. Sample-manipulation er ganske fleksibelt i SuperCollider, men det kræver en lille smule teknisk forberedelse, som gennemgås herunder. Derefter introducerer kapitlet til tre kompositionsstrategier, hvor vi komponerer med samples ved hjælp af pattern-teknikker: Algoritmisk produktion af dynamiske trommebeats, beatslicing, hvor vi klipper beats op i metrisk organiserede enheder, samt manipulation og sammensætning af samples til abstrakte lydcollager. Kaptitlet indeholder som altid øvelser inden for disse områder, hvor man kan bruge egne samples for at opnå særegne resultater.

# Samples i SuperCollider



SuperCollider kan fungere som en yderst fleksibel sample-maskine, hvor vi indlæser eksisterende lydfiler og arbejder med dem på forskellige måder. SuperCollider kan også skabe lydfiler, hvilket dog først gennemgås [senere](../10/a-optag-supercollider.md). Når vi arbejder med samples i SuperCollider, skal vi indlæse disse i en såkaldt `Buffer` på lydserveren. Derfra kan vi afspille samples med forskellige UGens: Herunder kigger vi først og fremmest på, hvordan man bruger `PlayBuf` samt hvordan den lidt mere fleksible `BufRd` fungerer.

Inden vi går i gang, kan det imidlertid være nyttigt at have de skiftende betydninger af ordet "sample" for øje. Det forudsættes herunder, at du er fortrolig med disse tre betydninger af ordet og kan forstå ud fra konteksten, hvad der menes.

- Den éne betydning af samplebegrebet er meget teknisk og angår hvordan lyd repræsenteres og bearbejdes i digitale systemer [@roads2023, p. 29]. Når man optager lyd via et lydkort, bliver lyden omdannet fra det analoge domæne (fx hvis vi optager lydsignalet fra en mikrofon) til det digitale domæne ved hjælp af en såkaldt analog-til-digital converter (ADC), hvor lydsignalet "måles" ("samples") mange gange pr. sekund. Det er her, udtrykket *samplerate* eller *samplingfrekvens* kommer i spil: Sampleraten for en lydfil definerer, hvor ofte lydsignalet oprindeligt blev målt, og dermed hvor hurtigt vi skal læse de enkelte målinger efter hinanden, når vi skal afspille filen. Almindelige samplerates inden for musik i dag er 44,1 kHz (CD-kvalitet), 48 kHz, 88,2 kHz, 96 kHz og 192 kHz. Målingens "opløsning", altså hvor fintfølende vores sampling af det analoge signal måler, kaldes lydoptagelsens *bitdybde* (på engelsk: *bit rate* eller *bit depth*). Man kan som en øvelse selv teste i SuperCollider, hvor mange valgmuligheder samplingen har ved bitdybder på hhv. 8, 16, 24 og 32 bit (med `2.pow(8)`, `2.pow(16)` osv.).
- En anden betydning af samplebegrebet er meget udbredt på nettet og knytter sig til de såkaldte sampler-musikinstrumenter [@kvifte2007, p. 107]. Her er der tale om korte lydoptagelser, der ofte emulerer akustiske musikinstrumenter. Det kan fx være lyden af et lilletromme-hit, et toneanslag på klaver eller guitar osv. Disse er ofte knyttet til interfaces som keyboards, elektroniske trommesæt/-maskiner, MIDI-instrumenter i DAW-programmer osv.
- En tredje betydning af sampling kan skelnes fra de første, og den vedrører den meget udbredte praksis, at komponister og producere inkorporerer større eller mindre dele af andre værker i deres egne værker [@kvifte2007, p. 107]. Dette har været en meget udbredt kunstnerisk strategi siden før ophavsretslovgivningens fremmarch og er fortsat særdeles udbredt i blandt andet populærmusikalske genrer, hvor særligt hiphoppen traditionelt har indebåret sampling i meget vid udstrækning. Der findes en del historisk og aktuel forskning om de musikformer og den såkaldte remixkultur, som baserer sig på sampling i denne betydning af ordet [@dyndahl2005; @kvifte2007; @miller2008; @navas2012; @rodgers2003; @sewell2014; @tillet2014].

## Indlæsning af lydfil i Buffer



For at arbejde med et sample/en lydfil, skal samplet indlæses i en såkaldt `Buffer`. En `Buffer` er et afgrænset område i lydserverens hukommelse, der fungerer lidt ligesom [en variabel](../01/a-variabler.md)[^1]. Derfor skal lydserveren også være bootet, før vi indlæser vores sample.

Vi foretager indlæsning af lydfiler med `Buffer.read(s, 'C:/lydfiler/minlydfil.wav')`, hvor første argument er lydserveren `s`, og andet argument er stien til den lydfil, vi ønsker at indlæse. Vi gemmer ofte resultatet af denne instruks i en variabel, så vi ved hjælp af variablen kan henvise til bufferen.

[^1]: I modsætning til de variabler, vi tidligere har arbejdet med, som hører til [fortolkeren](../01/a-brugerflade.md#brugerflade-fortolker-og-lydserver), er buffere nogle objekter, der tilhører lydserveren. Lydserveren har en liste med buffere og identificerer disse ved hjælp af deres unikke indekstal, som kan findes med method'en `.bufnum`. I praksis har vi sjældent brug for at arbejde direkte med bufferes nummer, da vi i stedet bruger almindelige variabler på fortolkeren til at holde styr på bufferne, og SuperCollider internt håndterer nummereringen af bufferne automatisk for os.

Som et eksempel kan man bruge et sample, der følger med SuperCollider (linje 2 herunder). Man kan også nemt arbejde med egne samples (se linje 5 herunder) - erstat blot `C:/lydfiler/galivanting.wav` med *stien* til din egen lydfil. En sti til en fil er blot en tekst-streng, som viser hvor i computerens mappehierarki, filen befinder sig. Her har jeg indlæst et udklip fra en oplæsning af digtet *'Urry*[^9] af C. J. Dennis [@dennis2015].

[^9]: Både digtet af C. J. Dennis og oplæsningen af Son of the Exiles tilhører det offentlige domæne. Oplæsningen kan findes i fuld længde via platformen [LibriVox](https://librivox.org/short-poetry-collection-142-by-various/).

```sc title="Indlæsning af lydfil i Buffer"
// Et indbygget sample indlæses i buffer
~sample = Buffer.read(s, Platform.resourceDir +/+ "sounds/a11wlk01.wav");

// En ekstern lydfil indlæses i buffer
~sample = Buffer.read(s, "C:/lydfiler/galivanting.wav");
```

![audio/ogg](../media/audio/08-urry-galivanting.ogg)
![audio/mpeg](../media/audio/08-urry-galivanting.mp3)

{==

Et tip til den dovne programmør: Stier til filer kan genereres ganske let i SuperCollider! Man kan trække filen ind i SuperColliders tekstfelt med musen, eller man kan copy-paste filen fra en mappe på din computer. Når du slipper en fil med musen eller taster Ctrl/Cmd-V på tastaturet for at sætte filen ind, vil SuperColliders IDE skrive filens sti, der hvor musemarkøren eller cursoren befinder sig. Smart, ikke sandt?

==}

Når lydfilen er indlæst i en `Buffer` under variabelnavnet `~sample`, som vist ovenfor, kan vi bruge forskellige [instance methods](../01/a-methods.md#instance-methods), til at vise grundlæggende oplysninger om samplet.

```sc title="Nyttige info-methods til buffere"
~sample.path;      // samplets oprindelige sti i filsystemet
// -> C:/lydfiler/galivanting.wav

~sample.duration;  // varighed, målt i sekunder
// -> 2.7284126984127

~sample.query;     // teknisk information om bufferen
// bufnum: 7
// numFrames: 120323
// numChannels: 1
// sampleRate: 44100.0

~sample.plot;      // visuel repræsentation
```

![Plot af sample indlæst i buffer](../media/figures/buffer-plot.png){ width="70%" }

Hvis du arbejder med mange lydfiler og bliver træt af at indlæse dem én ad gangen, kan du automatisere indlæsningen ved at skrive en [funktion](../01/a-funktioner.md), der [itererer over](../01/a-lister.md#iteration-over-lister) filerne i en mappe og indlæser dem en efter en. Alternativt kan du installere og anvende [udvidelsen *PolyBuf* af Mads Kjeldgaard](https://github.com/madskjeldgaard/PolyBuf), som gør netop dette.

### Indlæsning af enkeltkanaler fra lydfiler



Ønsker vi blot at indlæse én af flere kanaler i en lydfil, kan vi i stedet for method'en `Buffer.read` bruge `Buffer.readChannel` og under argumentet `channels` angive en liste med et tal for hver af de kanaler, vi ønsker at indlæse. Her er 0 typisk den venstre og 1 typisk den højre kanal.

```sc title="Indlæsning af lydfil i mono-buffer"
// Venstre kanal fra en ekstern lydfil indlæses i mono-buffer
~sampleV = Buffer.readChannel(s, "C:/lydfiler/minlydfil.wav", channels: [0]);

// Højre kanal fra en ekstern lydfil indlæses i mono-buffer
~sampleH = Buffer.readChannel(s, "C:/lydfiler/minlydfil.wav", channels: [1]);
```

## Sample-afspilning med PlayBuf



Den mest enkle måde at afspille samples på er at bruge UGen'en `PlayBuf`. Når vi gør det, er der to tekniske forhold, som er værd at huske på:

- **Sampleraten** i en given lydfil matcher ikke nødvendigvis lydserverens samplerate. Hvis lydserverens samplerate er 44,1 kHz, men lydfilen er produceret ved 48 kHz, vil afspilningen ske for langsomt. Det byder blandt andet, at tonehøjder og tempo ikke vil passe til det, vi forventer. Derfor har vi en særlig UGen, der kan tage højde for sådanne uoverensstemmelser, nemlig `BufRateScale`.
- **Antal samples:** Et lydsample eller en lydfil består som beskrevet ovenfor af et antal målinger ("samples"). Når vi bruger `PlayBuf`, arbejder vi med samplets varighed ud fra antallet af disse samples. Sammenholdt med sampleraten, dvs. hvor hurtigt vi skal læse disse samples, afspiller `PlayBuf` det sample, som er indlæst i bufferen. Vi kan imidlertid ikke bare gå ud fra antallet af enkeltsamples i en Buffer, da en buffer kan indeholde data fra lydfiler med et variabelt antal kanaler. En stereo-lydfil vil have dobbelt så mange samples som en mono-lydfil af samme varighed og med samme samplerate. De fleste filformater understøtter nu om dage mange kanaler, så hvordan tager vi højde for det? Jo, for at finde varigheden af en indlæst lydfil, målt i samples, kan vi bruge den dertil beregnede UGen `BufFrames`. Den giver os antallet af såkaldte *sample frames*, som er det samme, uanset hvor mange kanaler, bufferen indeholder.

Herunder fremgår, hvordan man indstiller argumenterne til `PlayBuf` og bruger `BufRateScale` samt `BufFrames` til at tage højde for det indlæste samples varighed og samplerate.

```sc title="PlayBuf-argumenter"
{
    PlayBuf.ar(
        // antal kanaler
        numChannels: 1,

        // variabel, der henviser til den ønskede Buffer
        bufnum: ~sample,

        // afspilningshastighed 1
        // BufRateScale tager højde for evt. mismatch mellem serverens og lydfilens respektive samplerates
        rate: 1 * BufRateScale.kr(~sample),

        // reset-trigger, kan bruges til at angive spring til startposition
        trigger: 0,

        // startposition måles i sample frames
        // BufFrames.kr giver det samplede antal sample frames i bufferen/lydfilen
        startPos: 0 * BufFrames.kr(~sample),

        // loop - start forfra, når vi rammer slutningen af bufferen (0 = nej, 1 = ja)
        loop: 1,

        // doneAction - hvad sker der, når vi rammer den sidste sample frame i bufferen?
        doneAction: Done.freeSelf
    )
}.play
```

![audio/ogg](../media/audio/08-galivanting-loop.ogg)
![audio/mpeg](../media/audio/08-galivanting-loop.mp3)

Vi kan modulere flere af `PlayBuf`s parametre ved hjælp af andre UGens. Herunder moduleres afspilningshastighed af henholdsvis `SinOsc` og `LFNoise1`.

```sc title="Modulation af sampleafspilning med LFO"
{
    PlayBuf.ar(1, ~sample,
        SinOsc.kr(2) * BufRateScale.kr(~sample)
    )
}.play;

{
    PlayBuf.ar(1, ~sample,
        LFNoise1.kr(1).exprange(0.5, 2) * BufRateScale.kr(~sample),
        loop: 1
    )
}.play;
```

![audio/ogg](../media/audio/08-lfo-playbuf.ogg)
![audio/mpeg](../media/audio/08-lfo-playbuf.mp3)

Med et [triggersignal](../04/c-ugens.md#triggere-og-delays), her skabt af UGen'en `Impulse`, kan vi springe hen til den position i bufferen, som er angivet med argumentet `startPos`.

```sc title="Spring til position i sample"
// Fast startposition - midt i bufferen
{
    PlayBuf.ar(1, ~sample,
        trigger: Impulse.kr(4),
        startPos: 0.4 * BufFrames.kr(~sample),
    )
}.play;

// Dynamisk startposition, moduleret af en LFO
{
    PlayBuf.ar(1, ~sample,
        trigger: Impulse.kr(4),
        startPos: BufFrames.kr(~sample) * LFTri.kr(0.05).unipolar,
    )
}.play
```

![audio/ogg](../media/audio/08-playbuf-reset.ogg)
![audio/mpeg](../media/audio/08-playbuf-reset.mp3)

## Ekstra fleksibilitet med BufRd



`BufRd` er mere fleksibel end `PlayBuf`, fordi den tillader, at vi styrer læsningen af data fra bufferen direkte med en anden UGen. Det svarer lidt til, at en pladespillers pickupnål aflæser den lyd, som er indpræget i en vinylplade. Men til forskel fra pladespillerens stabile rotationsbevægelse kan vi med et bredt udvalg af UGens kan flytte nålen rundt på meget forskellig vis. Til at styre afspilningspositionen angiver vi hertil en UGen under `BufRd.ar`'s argument `phase`.

Ofte anvendes UGen'en `Phasor` hertil, fordi den skaber en lineær rampe fra en start- til en slutværdi. Til disse to værdier kan vi angive henholdsvis 0 og bufferens samlede antal sample frames ved hjælp af `BufFrames`. Dette vil resultere i en afspilning af samplet præcist som det er indlæst i bufferen, når vi samtidig skalerer afspilningshastigheden med `BufRateScale` for at tage højde for eventuelt samplerate-mismatch, akkurat ligesom ved `PlayBuf`.

```sc title="Sample-afspilning med BufRd og Phasor"
{
    BufRd.ar(
        numChannels: 1,
        bufnum: ~sample,
        // phase-argumentet er afspilningspositionen, målt i sample frames
        phase: Phasor.ar(
            trig: 0, // ligesom PlayBuf's trigger-argument
            rate: BufRateScale.kr(~sample),
            start: 0,
            end: BufFrames.kr(~sample)
        ),
        loop: 1
    )
}.play;
```

Det interessante ved `BufRd` er imidlertid, at man frit kan anvende andre UGens end `Phasor`. Herunder moduleres afspilningspositionen i `BufRd` af henholdsvis en slagtøjsagtig envelope og en lavfrekvent støjgenerator, der bevæger sig tilfældigt.

```sc title="Envelope og tilfældighedsgenerator som pickupnål"
{
    var position = EnvGen.ar(Env.perc(0.1, 2)) * BufFrames.kr(~sample);
    BufRd.ar(1, ~sample, position, 1);
}.play;

{
    var position = LFNoise2.ar(2).range(0, BufFrames.kr(~sample));
    BufRd.ar(1, ~sample, position, 1);
}.play;
```

![audio/ogg](../media/audio/08-bufrd-modulation.ogg)
![audio/mpeg](../media/audio/08-bufrd-modulation.mp3)

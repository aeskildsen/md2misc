

# Øvelse: Brug af UGens



I denne øvelse øver man sig i at anvende, visualisere og modulere UGens.

## Blip båt



Afspil følgende lyde med peak-amplitude på 0.1:

1. Sinustone med frekvens på 220 Hz.
1. Savtakket bølgeform med frekvens på 100 Hz.
1. En firkantet bølgeform med frekvens på 350 Hz.

```sc title="Oscillatorfrekvenser"
{SinOsc.ar(   ) * 0.1}.play;
{     * 0.1}.play;
{     * 0.1}.play;
```

## Visualisering af bølgeform



SuperCollider kan plotte lyd-outputtet i en graf. Dette viser eksempelvis outputtet fra en `SinOsc` og en `LFTri`, målt over et stardard-tidsrum på 10 millisekunder.

```sc title="Visualisering af bølgeform"
{[
    SinOsc.ar(440),
    LFTri.ar(440)
]}.plot(0.010);
```

Brug `{}.plot`-teknikken ligesom ovenfor til at overveje følgende spørgsmål:

1. Hvad er forskellen på `Pulse.ar(width: 0.5)` og `Pulse.ar(width: 0.1)`?
1. Hvad er forskellen på `LFNoise0.kr(2)` og `LFNoise1.kr(2)`?

Tip: Når vi skal visualisere LFO-UGens, der som her svinger ved 2 Hz, får vi ikke meget syn for sagen ved at plotte over de 10 millisekunder, der som udgangspunkt anvendes med `.plot`. Plot i stedet over fx 3 sekunder med `{}.plot(3)`.

## Visualisering af frekvensspektrum



Vi kan vise SuperColliders lydlige output i frekvensdomænet med `s.freqscope;`

Brug `s.freqscope` til at besvare følgende spørgsmål:

1. Hvad kendetegner overtonespektrene for de forskellige bølgeformer fra opgaven *Blip båt* ovenfor?
1. Hvad styrer bevægelse af musen fra venstre til højre i nedenstående eksempel? Samt: Hvad kan vi herudfra konkludere om UG'enen `Blip`?

```sc title="Undersøgelse af UGen'en Blip"
{ Blip.ar(220, MouseX.kr(1,50)) * 0.1 }.play;
```

Har du mange ekstra vinduer åbne (fx fra ovenstående øvelse med plots), kan de lukkes på én gang med `Window.closeAll`.

## Modulation af lydstyrke (amplitude)



Anvend følgende UGens, [skaleret med method'en `.unipolar`](a-skalering.md), til at modulere amplituden i intervallet 0-1 for en savtakket bølgeform. Modulatorens frekvens vælges frit i intervallet 0-20 Hz.

1. `LFSaw` (savtakket bølgeform)
1. `LFPulse` (firkantet bølgeform)
1. `SinOsc` (sinusbølge)

```sc title="Amplitudemodulation med LFO"
{Saw.ar *   }.play;
```

## Modulation af tonehøjde (frekvens)



Når vi modulerer frekvens, er det typisk nødvendigt at justere modulatorens frekvens og outputrækkevidde. `.range` og `.exprange` er oplagte redskaber at styre en absolut modulation, og `.midiratio` (evt. kombineret med `.unipolar` eller `.bipolar`) er oplagt til at styre en relativ modulation af tonehøjde. Læs evt. nærmere herom i afsnittet om [skalering](a-skalering.md).

Modulér frekvensen for en savtakket oscillator med følgende UGens og på følgende måder:

1. Rutsjebane
    1. Brug `LFTri` som modulator.
    1. Tonens frekvens skal bevæge sig mellem 440 Hz og 880 Hz.
    1. Valgfri modulatorfrekvens under 20 Hz.
1. Tonespring
    1. Brug `LFPulse` som modulator.
    1. Tonens frekvens skal bevæge sig mellem 220 Hz og 330 Hz.
    1. Valgfri modulatorfrekvens under 20 Hz.
1. Vibrato
    1. Brug `SinOsc` som modulator.
    1. Tonens frekvens på 660 Hz skal moduleres 15 cent op og ned.
    1. Modulatorfrekvensen skal være 15 Hz.
1. Tilfældige frekvenser
    1. Brug `LFNoise0` som modulator.
    1. Tonens frekvens på 440 Hz skal moduleres i halvtonetrin op til en oktav op og ned.
    1. Modulatorfrekvensen skal være 8 Hz.

Vælg selv en passende frekvens mellem 0 Hz og 20 Hz til modulatoren.

```sc title="Frekvensmodulation" hl_lines="2"
{
    var modulator =   ;
    Saw.ar(modulator) * 0.1;
}.play;
```

## Bonusopgave: FM, AM, RM



Har du mod på at gå yderligere på opdagelse i modulationens potentialer, kan du med fordel dykke ned i nogle mere avancerede teknikker, hvor modulation på forskellig vis udgør kernen i klangdannelsen. Når modulation bevæger sig fra det lavfrekvente (under 20 Hz) til det hørbare frekvensbånd, sker der ganske interessante klanglige variationer.

1. Eksperimentér med eksemplerne på AM (Amplitude Modulation), RM (Ring Modulation) og FM (Frequency Modulation) fra kapitel 7 i Thor Magnussons [*Scoring Sound*](https://leanpub.com/ScoringSound/read#leanpub-auto-chapter-7---modulation) [-@magnusson2021].
1. Eksperimentér med eksemplerne på FM fra [Eli Fieldsteels glimrende video om emnet](https://www.youtube.com/watch?v=UoXMUQIqFk4&list=PLPYzvS8A_rTaNDweXe6PX4CXSGq4iEWYC&index=22). Kildekoden fra videoen findes [på github](https://github.com/elifieldsteel/SuperCollider-Tutorials/blob/master/full%20video%20scripts/21_script.scd).

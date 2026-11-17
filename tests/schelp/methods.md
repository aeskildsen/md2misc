---
summary: The class methods section, with argument tables
categories: Tests
---

## Description

A page with methods, argument tables and return values.

## Class methods

Two methods.

### *ar, *kr

Plays grains from a buffer.

| Argument | Range | What it does |
|:---|:---:|---|
| `bufnum` | | A mono buffer. **Silence** without one. |
| grainDur | seconds | The length of a grain. See [SinOsc](sc:Classes/SinOsc). |
| `mode` | `0` \| `1` | The mode: `a \| b` in code, and 1 \| 2 in text. |
| pan | −1 to 1 | > 0 is right, < 0 is left. |

Returns: an array of two channels.

### *new

Makes an instance.

Returns: a new instance.

## Examples

```supercollider
Md2miscTestMethods.ar(0, grainDur: 0.1);
```

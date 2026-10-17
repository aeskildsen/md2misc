## Escaping

Foo::bar and `a::b` and a || b and ## here, a lone # and | and a back\slash, a trailing backslash \

Characters that HTML needs to escape: a < b > c & 100% ~ ^ { } [ ] and "double" quotes with 'single' ones.

```supercollider
(
var a = "a::b"; // two colons in a string
a.postln;
)
::
||
```

```
// No language: SuperCollider.
1 + 1
```

```python
d = {"a": 1}
::
```

Closing paragraph with **bold text** and *italic text*.

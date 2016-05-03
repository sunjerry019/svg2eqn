# svg2eqn
Python script that converts SVG paths to parametric equations

```python conv2eqn.py f [--usepoly]```

```f``` is the filename <br />
```--usepoly``` uses polybeziers instead of cubicbeziers

## Dependencies
This script relies on ```sympy```, ```svg.path```, and ```argparse```

## Output
Without ```--usepoly```, the output is in latex, and the script compiles it using pdflatex. <br />
With ```--usepoly```, the output will be in plaintext.

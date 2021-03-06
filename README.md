# svg2eqn
[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

Python script that converts SVG paths to parametric equations

```python conv2eqn.py f [--usepoly]```

```f``` is the filename <br />
```--usepoly``` uses polybeziers instead of cubicbeziers

## Demo
![Demo](https://github.com/sunjerry019/svg2eqn/raw/master/demo.jpg "A heart!")

## Dependencies
This script relies on ```sympy```, ```svg.path```, and ```argparse```

## Output
Without ```--usepoly```, the output is in latex, and the script compiles it using pdflatex. <br />
With ```--usepoly```, the output will be in plaintext.

## Limitations
So far the code only works with lines, quadratic beziers and cubic beziers. Arcs are not yet supported.

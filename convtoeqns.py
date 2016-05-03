import sympy
import argparse
from xml.dom import minidom
import svg.path as sp
import os
from subprocess import call

def main():
	parser = argparse.ArgumentParser(description = "Converts SVG paths to parametric equations for plotting")
	parser.add_argument('file', metavar = 'f', help="SVG file to parse")
	parser.add_argument('--usepoly', action='store_true')
	args = parser.parse_args()
	Convert(args.file, args.usepoly)

class Convert():
	def __init__(self, filename, polybeziers = False):
		self.filename = filename
		self.dir = os.path.dirname(self.filename)
		self.name = os.path.basename(self.filename).split(".")[0]
		self.texfilename = os.path.join(self.dir, self.name + ".tex")
		self.outfilename = os.path.join(self.dir, self.name + ".paths")

		self.usepoly = polybeziers

		self.doc = minidom.parse(self.filename)
		self.paths = [path.getAttribute('d') for path in self.doc.getElementsByTagName('path')]
		self.splitPaths()
		self.convertPaths()
		self.printEqns()

		self.doc.unlink()

	def splitPaths(self):
		self.parsedPaths = []
		for path in self.paths:
			self.parsedPaths.append(sp.parse_path(path))
	def typ (self, seg):
		if isinstance(seg, sp.path.CubicBezier):
			return "CubicBezier"
		elif isinstance(seg, sp.path.Line):
			return "Line"
		elif isinstance(seg, sp.path.QuadraticBezier):
			return "QuadraticBezier"
		elif isinstance(seg, sp.path.Arc):
			return "Arc"
	def convertPaths(self):
		self.equations = []
		for path in self.parsedPaths:
			if self.usepoly:
				prevInstance = "Move"
				prevSegment = False
				self.polypaths = []
				for segment in path:
					if isinstance(segment, sp.path.CubicBezier) and prevInstance == ("CubicBezier"  or "QuadraticBezier") and segment.start == prevSegment.end:
						self.polypaths[-1].append(segment)
					else:
						self.polypaths.append([segment])
					prevInstance = self.typ(segment)
					prevSegment = segment

				for polysegment in self.polypaths:
					eqnsegment = []

					if len(polysegment) == 1:
						eqnsegment.append(self.convert(polysegment[0], self.typ(polysegment[0])))
					else:
						# combine those curvessss
						eqnsegment.append(self.convertToPoly(polysegment))

					self.equations.append(eqnsegment)
			else:
				eqnsegment = []
				for segment in path:
					eqnsegment.append(self.convert(segment, self.typ(segment)))
				self.equations.append(eqnsegment)
	def convert(self, seg, typ):
		start = {
			"x": seg.start.real,
			"y": seg.start.imag
		}

		end = {
			"x": seg.end.real,
			"y": seg.end.imag
		}

		t = sympy.symbols("t")
		if typ == "CubicBezier":
			c1 = {
				"x": seg.control1.real,
				"y": seg.control1.imag
			}

			c2 = {
				"x": seg.control2.real,
				"y": seg.control2.imag
			}

			xeqn = sympy.simplify(((1-t)**3)*(start["x"]) + (3*(1-t)**2)*t*(c1["x"]) + 3*(1-t)*(t**2)*(c2["x"]) + (t**3)*end["x"])
			yeqn = sympy.simplify(((1-t)**3)*(start["y"]) + (3*(1-t)**2)*t*(c1["y"]) + 3*(1-t)*(t**2)*(c2["y"]) + (t**3)*end["y"])

		elif typ == "Line":
			xeqn = sympy.simplify((1-t)*start["x"] + t*end["x"])
			yeqn = sympy.simplify((1-t)*start["y"] + t*end["y"])

		return [xeqn, yeqn]
	def convertToPoly(self, polyseg):
		points = []
		points.append({
			"x": polyseg[0].start.real,
			"y": polyseg[0].start.imag
		})

		for segment in polyseg:
			points.append({
				"x": segment.control1.real,
				"y": segment.control1.imag
			})

			if(self.typ(segment) == "CubicBezier"):
				points.append({
					"x": segment.control2.real,
					"y": segment.control2.imag
				})

			points.append({
				"x": segment.end.real,
				"y": segment.end.imag
			})

		t = sympy.symbols("t")
		xeqn = 0
		yeqn = 0
		i = 0;
		n = len(points) - 1
		for point in points:
			coeff = sympy.simplify(sympy.binomial(n, i)*(1-t)**(n-i)*t**i)
			xeqn += sympy.simplify(point["x"]*coeff)
			yeqn += sympy.simplify(point["y"]*coeff)
			i += 1
		simxeqn = sympy.simplify(xeqn)
		simyeqn = sympy.simplify(yeqn)

		return [simxeqn, simyeqn]


	def printEqns(self):
		if self.usepoly:
			self.outfile = open(self.outfilename, "w")

			counter = 0
			for segment in self.equations:
				self.outfile.write("=== Path " + str(counter + 1) + " ===\n")

				for equation in segment:
					self.outfile.write("x(t) = " + str(equation[0].evalf(11)) + "\n")
					self.outfile.write("y(t) = " + str(equation[1].evalf(11)) + "\n\n")
				counter += 1
			self.outfile.close()
			call(["cat", os.path.join(self.outfilename)])
		else:
			self.texfile = open(self.texfilename, "w")
			self.texfile.write("\\documentclass[a4paper]{report}\n")
			self.texfile.write("\\usepackage{amsmath}\n")
			self.texfile.write("\\usepackage[margin=0.5in]{geometry}\n")
			self.texfile.write("\\renewcommand{\\thesection}{\\arabic{section}}\n")
			self.texfile.write("\\begin{document}\n")
			self.texfile.write("Plot the following equations from $t=0$ to $t=1$:")

			counter = 0
			for segment in self.equations:
				self.texfile.write("\\section{Path " + str(counter + 1) + "}\n")

				for equation in segment:
					self.texfile.write("\\begin{align}\n")
					self.texfile.write("\\textrm{x}(t) &= " + sympy.latex(equation[0].evalf(11)) + "\\\\\n")
					self.texfile.write("\\textrm{y}(t) &= " + sympy.latex(equation[1].evalf(11)) + "\n")
					self.texfile.write("\\end{align}\n")

				counter += 1
			self.texfile.write("\\end{document}\n")

			self.texfile.close()
			self.compile()
	def compile(self):
		call(["pdflatex", "-output-directory=" + self.dir, self.texfilename])
		call(["rm", os.path.join(self.dir, self.name+".aux"), os.path.join(self.dir, self.name+".log")])
		call(["evince", os.path.join(self.dir, self.name+".pdf")])

main()

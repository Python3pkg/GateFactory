import math
import threading
import random
import itertools
import sys


class Factory():

	def __init__(self,input_dim,output_dim):
		self.input = self.rbl(input_dim)
		self.target = self.rbl(output_dim)
		self.output = []

		self.best = (0,1)
		self.best_depth = 0
		self.error = 1.0
		self.pool_length = int(math.sqrt(input_dim))
		self.pool = random.sample(range(input_dim),self.pool_length)

		self.mini_batch = []
		self.mini_batch_limit = int(math.sqrt(input_dim))
		self.level_counter = 0
		self.combination_counter = 0
		self.lock = False

		self.tex_content = ""

		self.stopper = False
		self.thread = None
		self.start()

	def _start(self):
		while not self.stopper:
			self.output = self.NAND(self.best)
			# level1
			if self.mini_batch:
				complex_combinations = []
				combinations = list(itertools.combinations_with_replacement(self.pool,2))
				for combination in combinations:
					if self.depth(combination) >= self.best_depth:
						complex_combinations.append(combination)
						error = 0
						error_old = 0
						divisor = 0
						for data in self.mini_batch:
							self.input = data[0]
							self.target = data[1]
							error_old += abs(self.NAND(self.best) - self.target[0])
							error += abs(self.NAND(combination) - self.target[0])
							divisor += 1
						if divisor != 0:
							if float(error) / divisor <= float(error_old) / divisor:
								self.best = combination
								self.error = float(error) / divisor
								print ""
								print self.best
								#print self.error
								self.best_depth = self.depth(self.best)
						self.combination_counter += 1
				if len(complex_combinations) >= self.pool_length:
					self.pool.extend(random.sample(complex_combinations,self.pool_length))
				else:
					self.pool.extend(random.sample(combinations,self.pool_length))
				for i in range(self.pool_length):
					self.pool[i] = random.sample(range(len(self.input)),1)[0]
				self.level_counter += 1
				#print self.pool
				#print "\n"

	def start(self):
		self.stopper = False
		if not self.thread:
			self.thread = threading.Thread(target=self._start)
			self.thread.start()
		print "Factory has been started"

	def stop(self):
		self.stopper = True
		self.thread = None
		print "Factory is now stopped"

	def load(self,input_arr,output_arr=None):
		if len(self.input) != len(input_arr):
			print "Size of the input array: " + str(len(input_arr))
			print "Size of the input of the factory: " + str(len(self.input))
			print "These values are not matching! Please fix it and try it again."
		else:
			self.input = input_arr
		if output_arr is None:
			self.mini_batch = []
			#self.target = []
		else:
			if len(self.target) != len(output_arr):
				print "Size of the output/target array: " + str(len(output_arr))
				print "Number of the output/target of the factory: " + str(len(self.target))
				print "These values are not matching! Please fix it and try it again."
			else:
				self.target = output_arr
				self.mini_batch.append([input_arr,output_arr])
				if len(self.mini_batch) > self.mini_batch_limit:
					self.mini_batch.pop(0)

	def NAND(self,duo):
		if isinstance(duo[0], tuple):
			left = self.NAND(duo[0])
		else:
			left = self.input[duo[0]]
		if isinstance(duo[1], tuple):
			right = self.NAND(duo[1])
		else:
			right = self.input[duo[1]]
		if not (left and right):
			return 1
		else:
			return 0

	def depth(self,expr):
	    if not isinstance(expr, tuple):
	        return 0
	    # this says: return the maximum depth of any sub-expression + 1
	    return max(map(self.depth, expr)) + 1

	#random binary list
	def rbl(self,n):
		return [random.randint(0,1) for b in range(1,n+1)]

	def generate_tex_file(self):
		self.tex_content = """\documentclass{article}
\usepackage{circuitikz}
\usepackage[width=122mm,left=12mm,paperwidth=1000mm,height=1000mm,top=12mm,paperheight=1000mm]{geometry}
\\begin{document}

\\begin{circuitikz}

\\node[nand port] at (0,0) (nand1) {};
\\node (o0) at (1,0) {$O_0$};
\draw (nand1.out) -- (o0);
"""
		self.logic_parser(self.best,0,0,1)

		self.tex_content += """
\end{circuitikz}

\end{document}"""

		with open("factory.tex", "w") as tex_file:
			tex_file.write(self.tex_content)

	def logic_parser(self,expression,x,y,gate):
		if isinstance(expression[0], tuple):
			gate += 1
			self.tex_content += "\n\\node[nand port] at ("+ str(x-2) +","+ str(y+1) +") (nand"+ str(gate) +") {};"
			self.tex_content += "\n\draw (nand"+ str(gate) +".out) -- (nand"+ str(gate-1) +".in 1);"
			self.logic_parser(expression[0],x-2,y+1,gate)
		else:
			self.tex_content += "\n\\node (i"+ str(expression[0]) +") at ("+ str(x-2) +","+ str(y+0.3) +") {$I_"+ str(expression[0]) +"$};"
			self.tex_content += "\n\draw (i"+ str(expression[0]) +") -- (nand"+ str(gate) +".in 1);"
			return True

		if isinstance(expression[1], tuple):
			gate += 1
			self.tex_content += "\n\\node[nand port] at ("+ str(x-2) +","+ str(y-1) +") (nand"+ str(gate) +") {};"
			self.tex_content += "\n\draw (nand"+ str(gate) +".out) -- (nand"+ str(gate-1) +".in 2);"
			self.logic_parser(expression[1],x-2,y-1,gate)
		else:
			self.tex_content += "\n\\node (i"+ str(expression[1]) +") at ("+ str(x-2) +","+ str(y-0.3) +") {$I_"+ str(expression[1]) +"$};"
			self.tex_content += "\n\draw (i"+ str(expression[1]) +") -- (nand"+ str(gate) +".in 2);"
			return True

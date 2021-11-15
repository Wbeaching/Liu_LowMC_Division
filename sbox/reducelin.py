from sbox.process_sbox import Sbox
import copy

class Reduce(Sbox):
	def __init__(self, filename, sbox):
		Sbox.__init__(self, sbox)
		self.filename = filename
		self.divtrial = self.CreateDivisionTrails()

	def ReadIne(self):
		"""
		Read the linear inequalites from filename to a list
		"""
		fileobj = open(self.filename, "r")
		ine = []
		for i in fileobj:
			ine.append(list(map(int, (i.strip()).split())))
		fileobj.close()
		return ine

	@staticmethod
	def Integer2Bitlist(n, l):
		"""
		Convert an integer n to its bitstring representation, and the length of the 
		bitstring is restricted to l. For an integer whose bitstring representation 
		with a length less than l, we add 0 ahead. This function return a list of 
		length l. 
		we assume the length of the bitstring representation of n is < 256
		"""
		s = list(map(int, list(format(n, "0256b"))))
		s = s[len(s) - l :]
		return s

	@staticmethod
	def ValueOfExpression(p, l):
		"""
		Evaluate the value of the linear inequality at point p, and l represents a linear inequality.
		"""
		assert len(p) + 1 == len(l), str(p)+str(l)
		# COPY the list, since we will modify the list and this will result in a 
		# change of the list outside the function.
		temp_p = copy.deepcopy(p)
		temp_p.append(1)
		return sum([x * y for (x, y) in zip(temp_p, l)])


	def InequalitySizeReduce(self):
		"""
		Given a set of points and the corresponding H-Representation, choose a 
		subset of inequalities from H-Representation which is equivalent to 
		describe the points.
		"""
		points = self.divtrial
		inequalities = self.ReadIne()
		assert len(points) > 0
		assert len(inequalities) > 0
		assert len(points[0]) + 1 == len(inequalities[0])
		length = len(points[0])
		# get all possible points in {0,1}^n
		apoints = [Reduce.Integer2Bitlist(i, length) for i in range(2**length)]
		# get the complementary set of points
		cpoints = [p for p in apoints if p not in points]
		ineq = copy.deepcopy(inequalities)
		# rineq stores the inequalities we choose
		rineq = []
		index = 0
		for p in ineq:
			if len(p) != length+1:
				print("有值小于%d！！！！" % (length+1))
		while len(cpoints) > 0 and len(ineq) > 0:
			temp_p = []
			temp_l = []
			# Fine the inequality which has the most points in cpoints that do
			# not satisfy this inequality 
			for l in ineq:
				temp = [p for p in cpoints if (Reduce.ValueOfExpression(p, l) < 0)]
				if len(temp) > len(temp_p):
					temp_p = temp
					temp_l = l
			if len(temp_p) == 0:
				print("空了")
				print(ineq)
				break
			for p in temp_p:
				cpoints.remove(p)
			rineq.append(temp_l)
			# print("rineq is --------------" + str(len(rineq)))
			# print(rineq)
			ineq.remove(temp_l)
			# print("index = " + str(index) + ", len(cpoints) = " + str(len(cpoints)))
			index += 1
		return rineq


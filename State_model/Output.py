class Output:
	def __init__(self):
		self.__indexes = []

	def add_index(self, index):
		self.__indexes.append(index)

	def get_indexes(self):
		return self.__indexes

	def get_number(self):
		return len(self.__indexes)

from dahuffman import HuffmanCodec
from bitstring import BitArray
from math import ceil, floor, log
import cPickle as pickle


OFFSET_ZERO = BitArray(bin='0')
OFFSET_ONE = BitArray(bin='1')

def get_decimal_places(d):
    r = d.split(".")
    if len(r) > 1:
        return len(r[1])
    return 0


class TinyCompressor:
    """This class holds data and methods for 
    a data compressor using LEC Algorithm"""

    table = {}
    decode_table = {}
    eof = 0
    __first_data = []
    __previous_data = []
    __data = []
    __data_ns = []
    __decimal_places = []
    __strings_table = {}
    __compressed_data = BitArray()
    __compressed_data_string = ""
    __data_length = 0

    __d_values = []
    codec = 0

    def __init__(self, decimal_places):
        self.__decimal_places = decimal_places[:]

    def get_n(self, d_value):
        if d_value == 0:
            return 0
        return int(floor(log(abs(d_value),2))) + 1

    def get_a(self,d_value,n_value):
        if d_value == 0:
            return ""
        if d_value < 0:
            return BitArray(int=d_value-1, length=20).bin[(-1)*n_value:]
        if d_value > 0:
            return BitArray(int=d_value, length=20).bin[(-1)*n_value:]

    def generate_data_list(self,inputfilename):
        first = True
        self.__first_data = []
        self.__previous_data = []
        self.__data_ns = []
        self.__data = []
        with open(inputfilename) as inputfile:
            for line in inputfile:
                linedata = line.split(",")
                self.__data_length = len(linedata)
                if (len(linedata) != len(self.__decimal_places)):
                    print "Length of decimal places different than length of data"
                    return #Should return an exception
                if first:
                    for i in range(len(linedata)):
                        self.__first_data.append(float(linedata[i]))
                    self.__previous_data = self.__first_data[:]
                    first = False
                else:
                    for i in range(len(linedata)):
                        value = (int(float(linedata[i]) * 10**self.__decimal_places[i]) - 
                                int(float(self.__previous_data[i]) * 10**self.__decimal_places[i]))
                        """if (i == 2):
                            print "Value =", value"""
                        self.__data.append(value)
                        self.__data_ns.append(self.get_n(value))
                    self.__previous_data = linedata[:]

        print "Data len =", len(self.__data)



    def generate_table(self,inputfilename):
        self.generate_data_list(inputfilename)
        self.codec = HuffmanCodec.from_data(self.__data_ns)
        self.table = self.codec.get_code_table()

        self.__strings_table = {}
        for symbol in self.table.keys():
            if not type(symbol) is int:
                self.eof = symbol
            bitsize, value = self.table[symbol]
            self.__strings_table[symbol] = bin(value)[2:].rjust(bitsize, '0')

    def encode_data(self, inputfilename, outputfilename):
        self.generate_data_list(inputfilename)
        self.__compressed_data_string = ""

        for i in range(len(self.__data)):
            self.__compressed_data_string += \
                self.__strings_table[self.__data_ns[i]] + \
                self.get_a(self.__data[i], self.__data_ns[i]) 

        #Add EOF
        self.__compressed_data_string += self.__strings_table[self.eof]

        self.__compressed_data = BitArray(bin=self.__compressed_data_string)
        #print "Compressed data to file:", self.__compressed_data.bin
        with open(outputfilename, 'wb') as outputfile:
            self.__compressed_data.tofile(outputfile)

    def build_values(self,inputfilename):
        print "Building values from", inputfilename

        compressed_bitarray = 0
        with open(inputfilename, 'rb') as compressedfile:
            compressed_bitarray = BitArray(compressedfile)

        #print "Compressed data from file:", compressed_bitarray.bin

        for k in self.__strings_table.keys():
            if (type(k) is int):
                self.decode_table[self.__strings_table[k]] = k
        possible_codes = set(self.decode_table.keys())

        #print "Decode table =", self.decode_table
        self.__d_values = []
        time_to_stop = False
        iteration = 0
        start_s = 0
        end_s = 1
        start_a = end_s
        end_a = 3
        n = 0
        s = 0
        a = 0

        while( not time_to_stop):
            if compressed_bitarray[start_s:end_s].bin in possible_codes:
                s = compressed_bitarray[start_s:end_s]
                n = self.decode_table[s.bin]
                start_a = end_s
                end_a = start_a + n # +1 ?


                if n == 0: #a = 0
                    self.__d_values.append(0)
                else:
                    a = compressed_bitarray[start_a:end_a]
                    if a[0]:
                        self.__d_values.append((OFFSET_ZERO+ a).int)
                    else:
                        self.__d_values.append((OFFSET_ONE+ a).int +1)
                start_s = end_a
            else:
                end_s += 1
            if end_s >= len(compressed_bitarray.bin):
                time_to_stop = True


    def decode_data(self,first_values, inputfilename, outputfilename):
        self.build_values(inputfilename)
        self.__values = []
        accumulator = first_values[:]
        print "len __d_values =", len(self.__d_values)
        """print "Data encoded =", self.__data
        print "Data decoded =", self.__d_values
        print "First values =", first_values"""
        """for i in range(len(self.__d_values)/len(accumulator)):
            self.__values.append(accumulator[:])
            for j in range(i, i*len(accumulator)+ len(accumulator)):
                print "(i,j) =",j-i*len(accumulator),j
                accumulator[j-i*len(accumulator)] += self.__d_values[j]"""
        self.__values.append(accumulator[:])
        for i in range(len(self.__d_values)):
            """if (i == 2):
                print "Value =", self.__d_values[i]"""
            """if((i%len(accumulator) == 1)):
                print self.__d_values[i]"""
            if self.__decimal_places[i%len(accumulator)] == 0:
                accumulator[i%len(accumulator)] += self.__d_values[i]
            else:
                accumulator[i%len(accumulator)] += float(self.__d_values[i]) \
                    / 10**self.__decimal_places[i%len(accumulator)]
            if ((i%len(accumulator)) == (len(accumulator)-1)):
                self.__values.append(accumulator[:])

        with open(outputfilename, 'wb') as outputfile:
            for value in self.__values:
                line = ",".join(
                    [("{:."+str(self.__decimal_places[i]) +"f}").format(float(value[i])) for i in range(len(value))])
                outputfile.write(line + '\n')



#example
input_file_name = "A.TXT"
output_file_name = "ENCODED.TXT"
decoded_file_name = "DECODED.TXT"

first_values = [300317183956,-22.86139,-43.22784,140,25,34,1] #a

t = TinyCompressor([0,5,5,0,0,0,0])
t.generate_table(input_file_name)

print "Table: "
t.codec.print_code_table()

t.encode_data(input_file_name, output_file_name)

t.decode_data(first_values, output_file_name, decoded_file_name)

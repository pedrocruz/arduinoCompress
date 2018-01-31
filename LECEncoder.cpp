#include "LECEncoder.h"

LECEncoder::LECEncoder(File &file){
  _file = file;
  //table =    {B1,        B0110,     B0000,     B010};
  //bitmasks = {B00000000, B00000001, B00000011, B00000111};

  _stream.value = 0;
  _stream.bits_number = 0;
}

/*LECEncoder::LECEncoder(int * codes_table){
  table = codes_table;
  _file = SD.open("O.TXT", FILE_WRITE);
  _stream.value = 0;
  _stream.bits_number = 0;
}*/

LECEncoder::LECEncoder(){
  _file = SD.open("O.TXT", FILE_WRITE);
  _stream.value = 0;
  _stream.bits_number = 0;
}

void LECEncoder::encode(int value){
  int n = get_n(value);
  int a = get_a(value, n);
  byte s = table[n] + a;
  Serial.print("Value = ");
  Serial.print(value);
  Serial.print(" n = ");
  Serial.print(n);
  Serial.print(" a = ");
  Serial.print(a);
  Serial.print(" s = ");
  Serial.println(s); 
  
  append_byte(s, s_size[n]);
}

int LECEncoder::append_byte(char value, int bits_number){
  Serial.print("appendByte "); Serial.print(value, BIN);
  Serial.print(" "); Serial.println(bits_number);


  int remaining_bits = bits_number;
  while (remaining_bits > 0){
    char tmp = 0;
    _stream.value = _stream.value << 1;

    tmp = value >> (remaining_bits - 1);

    _stream.value += (tmp & 1);
    remaining_bits --;
    _stream.bits_number ++;

    Serial.print("stream.bits = "); Serial.println(_stream.value, BIN);
    Serial.print("stream.bits_number = "); Serial.println(_stream.bits_number);
    if (_stream.bits_number >= 8){
      Serial.print("File = ");
      Serial.println(_file);
      Serial.print("print to file ");
      Serial.println(_stream.value, BIN);
      _file.write(_stream.value);
      //_file.println("HEEY?");
      _stream.bits_number = 0;
      _stream.value = 0;
    }
  }
}

int LECEncoder::get_n(int d_value){
  if (d_value > 128 || d_value < -128){
    return 9999;
  }

  byte value = d_value;
  if (d_value == 0){
      return 0;
  }

  int absolute = abs(d_value);
  int n = 8;
  for (byte mask = B10000000; mask > 0; mask >>=1){
    if (mask & absolute){
      break;
    }
    n--;
  }
  return n;
  //return int(floor(log(abs(value),2))) + 1;
}

int LECEncoder::get_a(int d_value, int n){
  int a = 0;
  a = bitmasks[n];
  a = d_value & a;

  if (d_value < 0)
    a--;
  return a;
}

LECEncoder::~LECEncoder(){
  Serial.println("end");
  if (_stream.bits_number > 0){
    Serial.println("flushing");
    _stream.value << (8 - _stream.bits_number);
    _file.write(_stream.value);
    _stream.bits_number = 0;
    _stream.value = 0;
  }
  _file.flush();
  _file.close();
}
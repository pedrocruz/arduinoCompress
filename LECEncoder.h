/*
  LECEncoder.h - Library for IoT compression.
  Created by Pedro Cruz, January 16, 2018.
  Released into the public domain.
*/
#ifndef LECEncoder_h
#define LECEncoder_h

#include "Arduino.h"
#include <SPI.h>
#include <SD.h>

/*table
0: 1
1: 011
2: 00
_EOF:010  */


struct BitStream{
  byte value;
  short bits_number;
};

class LECEncoder
{
  public:
    LECEncoder(File &file);
    LECEncoder();
    ~LECEncoder();
    void encode(int value);
    int table[4] =     {B1,        B0110,     B0000,     B010}; // Relates every n with a bitmask
    int s_size[4] =    {1,         4,         4,		 3}; // Number of bits in every s
    byte bitmasks[5] = {B00000000, B00000001, B00000011, B00000111, B00001111};

  private:
    int append_byte(char value, int bits_number);
    int get_n(int d_value);
    int get_a(int d_value, int n);
    int log2(int x);

    BitStream _stream;
    File _file;

    int _a;
};

#endif
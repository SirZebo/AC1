#ifndef IMAGE_PROCESSING_H
#define IMAGE_PROCESSING_H
#include "image.h"

Image* greyscale(Image* img);

Image* contrastImage(Image* img, unsigned char contrast);

float contrastFactor(unsigned char c);

int contrastAdjustment(unsigned char color, unsigned char c) ;

#endif
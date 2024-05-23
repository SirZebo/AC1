#ifndef IMAGE_H
#define IMAGE_H
#include <stddef.h>
#include "bitmap.h"

#pragma pack(1)
typedef struct RGB_STRUCT {
    unsigned char r;
    unsigned char g;
    unsigned char b;
    // unsigned char* padding;
} RGB;

typedef struct IMAGE_STRUCT {
    size_t height;
    size_t width;
    RGB* pixels;
} Image;

int imageSize(Image* img);

Image* openImage(Bitmap* bmp);

void freeImage(Image* image);

RGB getPixel(int col, int row, Image* img);

Image* imageCopy(Image* img);




#endif
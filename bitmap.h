#ifndef BITMAP_H
#define BITMAP_H
#include <stddef.h>

#pragma pack(1)
typedef struct BITMAP_STRUCT {
    // FileHeader
    char signature1;
    char signature2;
    int fileSize;
    int reserved;
    int dataOffset; // offset = headerSize + infoSize;

    // InfoHeader
    unsigned int size;
    unsigned int width;
    unsigned int height;
    unsigned short planes;
    unsigned short bitsPerPixel;
    unsigned int compression;
    unsigned int imageSize;
    unsigned int XpixelPerM;
    unsigned int YpixelPerM;
    unsigned int colorsUsed;
    unsigned int colorsImportant;

    // color table
    // char redIntensity;
    // char greenIntensity;
    // char blueIntensity;
    // char reservedIntensity;

    unsigned char* rasterData; // array of pixel RGB data
} Bitmap;

static const int BYTES_PER_PIXEL = 3;
static const int FILE_HEADER_SIZE = 14;
static const int INFO_HEADER_SIZE = 40;

Bitmap* loadBitmap(const char* imageFileName);


void generateBitmap(unsigned char* image, int height, int width, int pitch, const char* imageFileName);

Bitmap* openBitmap(const char* imageFileName);

void freeBitMap(Bitmap* bitmap);

// void writeBitmap(unsigned char* image, int height, int width, int pitch, const char* imageFileName);

// unsigned char* createBitmapFileHeader(int height, int width, int pitch, int paddingSize);

void writeBitmap(unsigned char* rgbs, int height, int width, const char* imageFileName);

unsigned char* createBitmapFileHeader(int height, int width);

unsigned char* createBitmapInfoHeader(int height, int width);

FILE* readFile(const char* imageFileName);

int convertSlice(const char *s, size_t a, size_t b);

#endif
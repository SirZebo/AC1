#include <stdio.h>
#include <stdlib.h>
#include "bitmap.h"
#include "image.h"

Image* openImage(Bitmap* bmp) {

    unsigned char* pixels = (unsigned char*) malloc(sizeof(unsigned char) * bmp -> imageSize);
    for (int i = 0; i < bmp -> imageSize; ++i) {
        pixels[i] = bmp -> rasterData[i]; 
    }

    Image* img = (Image*) malloc(sizeof(Image) * 1);
    img -> pixels = (RGB*) pixels;
    img -> height = bmp -> height;
    img -> width = bmp -> width;
    return img;
}

void freeImage(Image* img) {
    free(img -> pixels);
    free(img);
}

Image* greyscale(Image* img) {
    RGB* pixels = img -> pixels;
    for (int i = 0; i < imageSize(img); ++i) {
        int grey = (pixels[i].b + pixels[i].g + pixels[i].r) / 3;
        //printf("%d\n", pixels[i].g);
        pixels[i].b = grey;
        pixels[i].g = grey;
        pixels[i].r = grey;
    }
    return img;
    
}

Image* imageCopy(Image* img) {
    Image* copy = (Image*) malloc(sizeof(Image) * 1);
    RGB* pixels = (RGB*) malloc(sizeof(RGB) * img -> width * img -> height);
    for (int i = 0; i < imageSize(img); ++i) {
        pixels[i] = img -> pixels[i];
    }
    copy -> pixels = pixels;
    copy -> width = img -> width;
    copy -> height = img -> height;
    return copy; 
}

RGB getPixel(int col, int row, Image* img) {
    RGB* pixels = img -> pixels;
    RGB pixel = pixels[col * img -> width + row];
    return pixel;
}

int imageSize(Image* img) {
    return img -> width * img -> height;
}


#include <stdio.h>
#include "ImageProcessing.h"
#include "image.h"

Image* contrastImage(Image* img, unsigned char contrast) {
    RGB* pixels = img -> pixels;
    for (int i = 0; i < imageSize(img); ++i) {
        pixels[i].b = contrastAdjustment(pixels[i].b, contrast);
        pixels[i].g = contrastAdjustment(pixels[i].g, contrast);
        pixels[i].r = contrastAdjustment(pixels[i].r, contrast);
    }
    return img;
}

float contrastFactor(unsigned char c) {
    return  ((259 * (c + 255)) / (float) (255 * (259 - c)));
}

int contrastAdjustment(unsigned char color, unsigned char c) {
    int newColor = contrastFactor(c) * (color - 128) + 128;
    return newColor;
}
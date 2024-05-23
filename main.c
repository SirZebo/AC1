#include <stdio.h>
#include "bitmap.h"
#include "image.h"
#include "ImageProcessing.h"

int main() {
    char* file = "human.bmp";
    Bitmap* bmp = loadBitmap(file);
    Image* img = openImage(bmp);
    Image* grey = greyscale(imageCopy(img));
    Image* contrast = contrastImage(imageCopy(grey), 200);
    writeBitmap((unsigned char*) contrast -> pixels, contrast ->height, contrast-> width, "contrast.bmp");

    freeImage(img);
    freeImage(grey);
    freeImage(contrast);
    freeBitMap(bmp);


}

// int main() {
//     char* file = "untitled.bmp";
//     Bitmap* bmp = openBitmap(file);
//     printf("File size: %d\n", bmp -> fileSize);
//     printf("Image Size: %d\n", bmp -> imageSize);
//     printf("Bits per pixel: %d\n", bmp -> bitsPerPixel);
//     printf("Number of pixel: %d\n", bmp -> height * bmp -> width);

//     Image* img = openImage(bmp);
//     Image* grey = greyscale(imageCopy(img)); 

//     Image* contrast = contrastImage(imageCopy(img), 25);
//     printf("%d %d %d\n", getPixel(3, 1, contrast).b, getPixel(3, 1, contrast).g, getPixel(3, 1, contrast).r );
    
//     char* greyscale = "greyscale.bmp";

    
//     freeBitMap(bmp);
//     freeImage(img);
//     freeImage(grey);
//     freeImage(contrast);
    
//     return 0;
// }
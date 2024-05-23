#include <stdio.h>
#include <stdlib.h>
#include "bitmap.h"

// void writeBitmap(unsigned char* image, int height, int width, int pitch, const char* imageFileName) {
//     unsigned char padding[3] = {0, 0, 0};
//     int paddingSize = (4 - (/*width*BYTES_PER_PIXEL*/ pitch) % 4 ) % 4; // draw this out and visualize
//     unsigned char* fileHeader = (unsigned char*) createBitmapFileHeader(height, width, pitch, paddingSize);
//     unsigned char* infoHeader = (unsigned char*) createBitmapInfoHeader(height, width);

//     FILE* imageFile = fopen(imageFileName, "wb");

//     fwrite(fileHeader, 1, FILE_HEADER_SIZE, imageFile);
//     fwrite(infoHeader, 1, INFO_HEADER_SIZE, imageFile);

//     for (int i = 0; i < height; ++i) {
//         fwrite(image + (i * pitch), BYTES_PER_PIXEL, width, imageFile);
//         fwrite(padding, 1, paddingSize, imageFile);
//     }

//     fclose(imageFile);
// }

// unsigned char* createBitmapFileHeader(int height, int width, int pitch, int paddingSize) {

//     int fileSize = FILE_HEADER_SIZE + INFO_HEADER_SIZE + (/*BYTES_PER_PIXEL* width */ pitch + paddingSize);
//     static unsigned char fileHeader[] = {
//         0, 0, // signature
//         0, 0, 0, 0, // image file size in bytes
//         0, 0, 0, 0, // reserved
//         0, 0, 0, 0, // start of pixel array
//     };

//     fileHeader[0] = (unsigned char) ('B'); // BM as signature, bitmap
//     fileHeader[1] = (unsigned char) ('M');
//     fileHeader[2] = (unsigned char) (fileSize);
//     fileHeader[3] = (unsigned char) (fileSize >> 8);
//     fileHeader[4] = (unsigned char) (fileSize >> 16);
//     fileHeader[5] = (unsigned char) (fileSize >> 24);
//     fileHeader[10] = (unsigned char) (FILE_HEADER_SIZE + INFO_HEADER_SIZE); // check this

//     return fileHeader;
// }

void writeBitmap(unsigned char* rgbs, int height, int width, const char* imageFileName) {
    unsigned char* fileHeader = (unsigned char*) createBitmapFileHeader(height, width);
    unsigned char* infoHeader = (unsigned char*) createBitmapInfoHeader(height, width);

    FILE* imageFile = fopen(imageFileName, "wb");

    fwrite(fileHeader, 1, FILE_HEADER_SIZE, imageFile);
    fwrite(infoHeader, 1, INFO_HEADER_SIZE, imageFile);
    fwrite(rgbs, 3, width * height, imageFile);

    fclose(imageFile);
}

unsigned char* createBitmapFileHeader(int height, int width) {

    int fileSize = FILE_HEADER_SIZE + INFO_HEADER_SIZE + (width * height * 3);
    static unsigned char fileHeader[] = {
        0, 0, // signature
        0, 0, 0, 0, // image file size in bytes
        0, 0, 0, 0, // reserved
        0, 0, 0, 0, // start of pixel array
    };

    fileHeader[0] = (unsigned char) ('B'); // BM as signature, bitmap
    fileHeader[1] = (unsigned char) ('M');
    fileHeader[2] = (unsigned char) (fileSize);
    fileHeader[3] = (unsigned char) (fileSize >> 8);
    fileHeader[4] = (unsigned char) (fileSize >> 16);
    fileHeader[5] = (unsigned char) (fileSize >> 24);
    fileHeader[10] = (unsigned char) (FILE_HEADER_SIZE + INFO_HEADER_SIZE ); // check this

    return fileHeader;
}

unsigned char* createBitmapInfoHeader(int height, int width) {
    int imageSize = height * width * 3;
    int horizontalResolution = 7559;
    int verticalResolution = 7559;
    printf("image size %d\n", imageSize);
    static unsigned char infoHeader[] = { // check why use static here
        0, 0, 0, 0, // header size
        0, 0, 0, 0, // image width
        0, 0, 0, 0, // image height
        0, 0, // number of color planes
        0, 0, // bits per pixel
        0, 0, 0, 0, // compression
        0, 0, 0, 0, // image size
        0, 0, 0, 0, // horizontal resolution
        0, 0, 0, 0, // vertical resolution
        0, 0, 0, 0, // colors in color table
        0, 0, 0, 0, // important color count
    };
    infoHeader[0] = (unsigned char) (INFO_HEADER_SIZE);
    infoHeader[4] = (unsigned char) (width);
    infoHeader[5] = (unsigned char) (width >> 8); // 1 byte has 8 bits
    infoHeader[6] = (unsigned char) (width >> 16);
    infoHeader[7] = (unsigned char) (width >> 24);
    infoHeader[8] = (unsigned char) (height);
    infoHeader[9] = (unsigned char) (height >> 8);
    infoHeader[10] = (unsigned char) (height >> 16);
    infoHeader[11] = (unsigned char) (height >> 24);
    infoHeader[12] = (unsigned char) (1);
    infoHeader[14] = (unsigned char) (24);
    infoHeader[20] = (unsigned char) (imageSize);
    infoHeader[21] = (unsigned char) (imageSize >> 8);
    infoHeader[22] = (unsigned char) (imageSize >> 16);
    infoHeader[23] = (unsigned char) (imageSize >> 24);
    infoHeader[24] = (unsigned char) (horizontalResolution);
    infoHeader[25] = (unsigned char) (horizontalResolution >> 8);
    infoHeader[26] = (unsigned char) (horizontalResolution >> 16);
    infoHeader[27] = (unsigned char) (horizontalResolution >> 24);
    infoHeader[28] = (unsigned char) (verticalResolution);
    infoHeader[29] = (unsigned char) (verticalResolution >> 8);
    infoHeader[30] = (unsigned char) (verticalResolution >> 16);
    infoHeader[31] = (unsigned char) (verticalResolution >> 24);
    return infoHeader;

}

Bitmap* loadBitmap(const char* imageFileName) {
    FILE* file = readFile(imageFileName);
    Bitmap* bmp = (Bitmap*) malloc ( (FILE_HEADER_SIZE + INFO_HEADER_SIZE) * sizeof(char) + sizeof(unsigned char*) );
    fread( (char*) bmp, sizeof(char), FILE_HEADER_SIZE + INFO_HEADER_SIZE, file );
    printf("%d\n", bmp -> dataOffset);

    unsigned int size = ((((bmp->width * bmp->height) + 31) & ~31) / 8) * bmp->height;
    printf("size: %d\n", size);
    printf("image size: %d\n", bmp -> imageSize);
    printf("size / image size: %d\n", size / bmp -> imageSize);
    printf("image pixels: %d\n", bmp -> width * bmp -> height);
    bmp->rasterData = malloc(size);
    fread(bmp->rasterData, sizeof(unsigned char), size, file);
    fclose(file);

    return bmp;
}

Bitmap* openBitmap(const char* imageFileName) {

    FILE* file = readFile(imageFileName);
    fseek(file, 0, SEEK_END); // jump to the end of file
    size_t fileLen = ftell(file); // get the current byte offset in the file
    rewind(file); // jump back to the beginning of the file

    // can be improved
    if (fileLen < FILE_HEADER_SIZE + INFO_HEADER_SIZE + sizeof(unsigned char*)) {
        printf("Unable to open BMP file");
        return (Bitmap*) malloc ( (FILE_HEADER_SIZE + INFO_HEADER_SIZE) * sizeof(char) + sizeof(unsigned char*) );
    }

    Bitmap* bmp = (Bitmap*) malloc ( (FILE_HEADER_SIZE + INFO_HEADER_SIZE) * sizeof(char) + sizeof(unsigned char*) );
    fgets( (char*) bmp, FILE_HEADER_SIZE + INFO_HEADER_SIZE, file );
    fseek(file, FILE_HEADER_SIZE + INFO_HEADER_SIZE, SEEK_SET);

    unsigned char* rasterData = (unsigned char*) malloc (bmp -> imageSize * sizeof(unsigned char));
    fgets(rasterData, bmp -> imageSize, file);

    fclose(file);

    //Bitmap* bmp = (Bitmap*) header;
    bmp -> rasterData = rasterData;
    return bmp;
}
    
    /*
    FILE* file = readFile(imageFileName);
    fseek(file, 0, SEEK_END); // jump to the end of file
    size_t fileLen = ftell(file); // get the current byte offset in the file
    rewind(file); // jump back to the beginning of the file

    buffer = (char*) malloc(fileLen * sizeof(char)); //  Enough memory for the file
    fread(buffer, fileLen, 1, file); // Read in the entire file
    fclose(file); close the file
    */
    


FILE* readFile(const char* imageFileName) {
    FILE* file = fopen(imageFileName, "r");

    if (file == NULL) {
        printf("File does not exist!");
    }
    return file;
}

void freeBitMap(Bitmap* bitmap) {
    free(bitmap -> rasterData);
    free(bitmap);
}

// int convertSlice(const char *s, size_t a, size_t b) {
//     int val = 0;
//     while (a < b) {
//        val = val * 10 + s[a++] - '0';
//     }
//     return val;
// }
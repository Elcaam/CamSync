// ==============================
// CamSync Encryption Tool
//
// This program performs AES-256-CBC encryption and decryption
// on binary files using OpenSSL. For development/testing purposes,
// the key and IV are hardcoded and shared by both encrypt and decrypt.
//
// Usage: CamSync.exe encrypt input.txt output.enc
//        CamSync.exe decrypt input.enc output.txt
// ==============================

#include <iostream>          
#include <fstream>           
#include <vector>            
#include <openssl/evp.h>     // OpenSSL's high-level encryption/decryption API
#include <openssl/err.h>     // for printing human-readable OpenSSL errors

// Defining key and IV sizes for AES-256-CBC
const int KEY_SIZE = 32;     // 32 bytes = 256-bit encryption key
const int IV_SIZE = 16;      // 16 bytes = 128-bit IV required for CBC mode

// Helper function to print detailed OpenSSL errors 
void printErrors(const std::string& context) {
    std::cerr << "[OpenSSL] Error during: " << context << std::endl;
    ERR_print_errors_fp(stderr);
}

// ================================================================
// Encrypts a file using AES-256-CBC
// inputPath  -> plaintext file path to encrypt
// outputPath -> path to write encrypted output
// key, iv    -> must be fixed or shared between encrypt/decrypt
// ==============================================================

bool encryptFile(const std::string& inputPath, const std::string& outputPath,
                 const unsigned char* key, const unsigned char* iv) {

    // Opening source file to read and output file to write in binary mode
    std::ifstream input(inputPath, std::ios::binary);
    std::ofstream output(outputPath, std::ios::binary);
    if (!input || !output) {
        std::cerr << "❌ Nah nah... Could not open input or output file.\n";
        return false;
    }

    // Creating and initializing the OpenSSL encryption context
    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        printErrors("creating encryption context");
        return false;
    }

    // Set up the context to use AES-256-CBC with provided key and IV
    if (!EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), nullptr, key, iv)) {
        printErrors("initializing encryption");
        EVP_CIPHER_CTX_free(ctx);
        return false;
    }

    // Buffers for reading plaintext and writing encrypted data
    const size_t bufferSize = 4096;
    std::vector<unsigned char> buffer(bufferSize);
    std::vector<unsigned char> outBuffer(bufferSize + EVP_MAX_BLOCK_LENGTH);
    int outLen = 0;

    // Read file in chunks, encrypt each chunk, write to output file
    while (input.good()) {
        input.read(reinterpret_cast<char*>(buffer.data()), bufferSize);
        std::streamsize bytesRead = input.gcount();

        if (!EVP_EncryptUpdate(ctx, outBuffer.data(), &outLen, buffer.data(), static_cast<int>(bytesRead))) {
            printErrors("encrypting block");
            EVP_CIPHER_CTX_free(ctx);
            return false;
        }

        output.write(reinterpret_cast<char*>(outBuffer.data()), outLen);
    }

    // Finalize encryption: handles padding and flushes final block
    if (!EVP_EncryptFinal_ex(ctx, outBuffer.data(), &outLen)) {
        printErrors("finalizing encryption");
        EVP_CIPHER_CTX_free(ctx);
        return false;
    }

    output.write(reinterpret_cast<char*>(outBuffer.data()), outLen);
    EVP_CIPHER_CTX_free(ctx);
    return true;
}

// ==============================
// Decrypts a file encrypted with AES-256-CBC
// inputPath  -> encrypted file (.enc)
// outputPath -> restored plaintext file path
// key, iv    -> must match exactly what was used to encrypt
// ============================================================
bool decryptFile(const std::string& inputPath, const std::string& outputPath,
                 const unsigned char* key, const unsigned char* iv) {

    std::ifstream input(inputPath, std::ios::binary);
    std::ofstream output(outputPath, std::ios::binary);
    if (!input || !output) {
        std::cerr << "❌ NOPE!!!!!!!!!!! Could not open input or output file for decryption.\n";
        return false;
    }

    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        printErrors("creating decryption context");
        return false;
    }

    if (!EVP_DecryptInit_ex(ctx, EVP_aes_256_cbc(), nullptr, key, iv)) {
        printErrors("initializing decryption");
        EVP_CIPHER_CTX_free(ctx);
        return false;
    }

    const size_t bufferSize = 4096;
    std::vector<unsigned char> buffer(bufferSize);
    std::vector<unsigned char> outBuffer(bufferSize + EVP_MAX_BLOCK_LENGTH);
    int outLen = 0;

    // Read encrypted file in chunks and decrypt
    while (input.good()) {
        input.read(reinterpret_cast<char*>(buffer.data()), bufferSize);
        std::streamsize bytesRead = input.gcount();

        if (!EVP_DecryptUpdate(ctx, outBuffer.data(), &outLen, buffer.data(), static_cast<int>(bytesRead))) {
            printErrors("decrypting block");
            EVP_CIPHER_CTX_free(ctx);
            return false;
        }

        output.write(reinterpret_cast<char*>(outBuffer.data()), outLen);
    }

    // Finalize decryption: verifies padding and final bytes
    if (!EVP_DecryptFinal_ex(ctx, outBuffer.data(), &outLen)) {
        printErrors("finalizing decryption");
        EVP_CIPHER_CTX_free(ctx);
        return false;
    }

    output.write(reinterpret_cast<char*>(outBuffer.data()), outLen);
    EVP_CIPHER_CTX_free(ctx);
    return true;
}

// ==============================
// Entry Point
// ==============================
int main(int argc, char* argv[]) {
    // Check for 3 required command line arguments
    if (argc != 4) {
        std::cerr << "Usage: CamSync.exe <encrypt|decrypt> <input> <output>\n";
        return 1;
    }

    // Get mode and file paths from user input
    const std::string mode = argv[1];
    const std::string inputFile = argv[2];
    const std::string outputFile = argv[3];

    // Hardcoded key and IV — and yes, it's not ideal 
    unsigned char key[KEY_SIZE] = {
        0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
        0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff,
        0x10, 0x21, 0x32, 0x43, 0x54, 0x65, 0x76, 0x87,
        0x98, 0xa9, 0xba, 0xcb, 0xdc, 0xed, 0xfe, 0x0f
    };

    unsigned char iv[IV_SIZE] = {
        0x0f, 0x1e, 0x2d, 0x3c, 0x4b, 0x5a, 0x69, 0x78,
        0x87, 0x96, 0xa5, 0xb4, 0xc3, 0xd2, 0xe1, 0xf0
    };

    // Choosing operation mode t
    if (mode == "encrypt") {
        std::cout << "🔐 Encrypting " << inputFile << " → " << outputFile << std::endl;
        return encryptFile(inputFile, outputFile, key, iv) ? 0 : 1;
    } else if (mode == "decrypt") {
        std::cout << "🔓 Decrypting " << inputFile << " → " << outputFile << std::endl;
        return decryptFile(inputFile, outputFile, key, iv) ? 0 : 1;
    } else {
        std::cerr << "❌ Invalid mode. Use 'encrypt' or 'decrypt'.\n";
        return 1;
    }
}

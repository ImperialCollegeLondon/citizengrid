
#include <string.h>
#include <iostream>
#include <glib.h>
#include "stdlib.h"
#include "b64/encode.h"
#include "b64/decode.h"
using namespace std;

// Include the contextiso header
#include "include/contextiso.h"

#define BUFFER 2048

// Usage example of libcontextiso
int main(int argc, char *argv[]) {

    // The contextualization file content in two parts before encoding
    const char *config_file1 = "[amiconfig]\nplugins=cernvm\n\n[cernvm]\ncontextualization_key=cfcbde8ad2d4431d8ecc6dd801015252\nliveq_queue_id=";
    char *context_config = (char*)malloc(BUFFER);
    char *context_config_b64 = (char*)malloc(BUFFER);
    int base64_len = 0;
    int encoded_bytes = 0;
    FILE *outputFile;
    char *base64_output;

    if(argc != 3) {
        printf("\nUsage: cg_vams_iso_gen <group ID> <output file>\n\n");
        exit(0);
    }

    strcat(context_config, config_file1);
    strcat(context_config, argv[1]);
    strcat(context_config, "\n");
    base64_len = strlen(context_config);

    cout << "Context file:\n" << context_config << "\n\n" << "Output file: " << argv[2] << "\nBase 64 length: " << base64_len << "\n\n";

    base64_output = g_base64_encode((guchar*)context_config, base64_len);
    cout << "B64 content: " << base64_output << "\n";

    // The contents of the contextualization file
    const char * dataStart = "EC2_USER_DATA=\"";
    const char * dataEnd = "\"\nONE_CONTEXT_PATH=\"/var/lib/amiconfig\"\n";
    strcat(context_config_b64, dataStart);
    strcat(context_config_b64, base64_output);
    strcat(context_config_b64, dataEnd);

    cout << "Context data: " << context_config_b64 << "\nContext data length: " << strlen(context_config_b64) << "\n";

    // Build a CD-ROM image with the given context.sh
    char * cdrom = build_simple_cdrom(
        "CONFIGDISK", 
        "CONTEXT.SH",
        context_config_b64,
        strlen(context_config_b64)
        );
    
    // Dump the results to stdout
    cout.write(cdrom, CONTEXTISO_CDROM_SIZE);
    
    // Write the ISO content to a file
    outputFile = fopen(argv[2], "w");
    fwrite (cdrom, sizeof(char), CONTEXTISO_CDROM_SIZE, outputFile);
    fclose(outputFile);

    // Free memory
    free(context_config);
    free(context_config_b64);

    // Success
    return 0;
}

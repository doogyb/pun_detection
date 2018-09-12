#include <stdio.h>
#include <stdlib.h>
#include <zlib.h>
#include <string.h>

#define FIRST_TOKEN 2

int main(int argc, char *argv[]) {

  const char* path = argv[1];

  int i = 2;
  int LAST_TOKEN = argc;
  int found = 0;

  gzFile gfile = gzopen(path, "rb");
  if (gfile == NULL) {
    printf("0\n");
    return 0;
  }
  char *line = malloc(100);
  char *token;
  while (gzgets(gfile, line, 100) != NULL) {

    char *tmpline = strdup(line);
    while ((token = strsep(&tmpline, " \t")) != NULL) {

      if (i == LAST_TOKEN) {
        printf("%s", token);
        found=1;
        break;
      }
      if (strcmp(token, argv[i++]) != 0) {
        i=FIRST_TOKEN;
        break;
      }
      else {
      }

    }
    if (found == 1)
      break;
  }
  if (found == 0) {
    printf("0\n");
  }
    return 0;
}

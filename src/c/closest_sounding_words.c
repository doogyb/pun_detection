#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Phoneme {
    char word[30];
    char **phonemes;
    int ph_len;
} Phoneme;

#define CMU_LENGTH 123455
#define MAX_RESULT 1000
Phoneme entries[CMU_LENGTH];
char closest_words[MAX_RESULT][30];
int count = 0;

void readFile() {

    FILE *fp;
    fp = fopen("/home/doogy/Projects/pun_detection/data/cmusimpler.txt", "r");
    if (fp == NULL) {
        fprintf(stderr, "Could not open file\n");
        exit(EXIT_FAILURE);
    }

    size_t len = 0;
    ssize_t read;
    char* line=NULL;
    int count=0;

    while ((read = getline(&line, &len, fp)) != -1) {
        Phoneme ph;
        unsigned int i;
        for (i=0; i<len; i++) {
            if (line[i] == '\t') {
                ph.word[i] = '\0';
                break;
            }
            ph.word[i] = line[i];
        }
        i++;
        unsigned int n_ph = 0;
        ph.phonemes = (char **) malloc(sizeof(char**));
        while (i<read-2) {

            ph.phonemes = (char **) realloc(ph.phonemes, (n_ph + 1) * sizeof(*ph.phonemes));

            if (ph.phonemes == NULL)
                printf("Failed to allocate memory\n");
            ph.phonemes[n_ph] = (char *) malloc(sizeof(char) * 3);
            if (ph.phonemes[n_ph] == NULL) {
                printf("Failed to allocate memeory\n");
            }
            if (line[i+1] == ',') {
                ph.phonemes[n_ph][0] = line[i];
                ph.phonemes[n_ph][1] = '\0';
                i+=2;

            }
            else {
                ph.phonemes[n_ph][0] = line[i];
                ph.phonemes[n_ph][1] = line[i+1];
                ph.phonemes[n_ph][2] = '\0';


                i+=3;
            }
            n_ph++;
        }
        ph.ph_len = n_ph;
        entries[count++] = ph;
    }
}

Phoneme *find_phoneme(char* word) {
    int i;
    for (i=0; i<CMU_LENGTH; i++)
        if (strcmp(entries[i].word, word) == 0)
            return &entries[i];
    return NULL;
}

int min(int a, int b) {
    if (a < b)
        return a;
    return b;
}

int levenshtein_distance(Phoneme ph1, Phoneme ph2) {
    if (ph1.ph_len < ph2.ph_len)
        return levenshtein_distance(ph2, ph1);
    if (ph2.ph_len == 0)
        return ph1.ph_len;

    int v0[ph2.ph_len+1], v1[ph2.ph_len+1];
    int i, j;
    for (i=0; i<ph2.ph_len+1; i++)
        v0[i] = i;

    for (i=0; i<ph1.ph_len; i++) {
        v1[0] = i+1;
        for (j=0; j < ph2.ph_len; j++) {
            int cost = (strcmp(ph1.phonemes[i], ph2.phonemes[j])==0) ? 0 : 1;
            v1[j+1] = min(min(v1[j] + 1, v0[j+1] + 1), v0[j] + cost);
        }
        for (j = 0; j<ph2.ph_len+1; j++)
            v0[j] = v1[j];
    }
    return v1[ph2.ph_len];
}

void get_closest_sounding_words(Phoneme *search_word, int threshold) {
//    Phoneme *search_word = find_phoneme(word);

//    printf("Phoneme representation: %s\n", search_word->phonemes[0]);
//    printf("Got here\n");
//    if (search_word == NULL) {
//        return;
//    }
    if (threshold == 0)
        threshold = search_word->ph_len > 5 ? 2 : 1;
//    printf("Threshold: %d\n", threshold);
    int i;
    // possibly increase threshold when words begin with same phoneme
    for (i=0; i<CMU_LENGTH; i++) {
        if (strcmp(search_word->word, entries[i].word)!=0) {
            if (levenshtein_distance(*search_word, entries[i]) <= threshold) {
                strcpy(closest_words[count++], entries[i].word);
                if (count == MAX_RESULT-1)
                    return;
    }
        }
            }
}

int main(int argc, char **argv) {
    readFile();
    // Note: doesn't work with apostrophes...
    int threshold;
    char *endptr;
    if (argc == 3)
        threshold = 0;
    else
        threshold = strtol(argv[3], &endptr, 10);

    Phoneme ph;
    strcpy(ph.word, argv[1]);
    ph.phonemes = (char **) malloc(sizeof(char**));
    // second argument is phoneme representation...


    char *p = strtok(argv[2], "/");
    unsigned int tokens = 0;
    while (p != NULL)
    {
        ph.phonemes = (char**) realloc(ph.phonemes, ++tokens * sizeof(ph.phonemes));
        ph.phonemes[tokens-1] = p;
        p = strtok (NULL, "/");
    }
    ph.ph_len = tokens;
    get_closest_sounding_words(&ph, threshold);
    int i;
    for (i=0; i<count; i++) {
        printf("%s\n", closest_words[i]);
    }
    // Phoneme *ph1 = find_phoneme("liken");
    // Phoneme *ph2 = find_phoneme("lichen");
    // printf("%d\n", levenshtein_distance(*ph1, *ph2));
    return 0;
}

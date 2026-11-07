/* Placeholder program for students to debug. Replace with your own sources.
 * Everything in challenge/ is compiled in the build stage of the Dockerfile
 * and copied to /opt/challenge (read-only for the student). */
#include <stdio.h>
#include <string.h>

static int checksum(const char *s) {
    int sum = 0;
    for (; *s; s++) sum += (unsigned char)*s;
    return sum;
}

static void greet(const char *name) {
    char buf[16];
    strcpy(buf, name);          /* no bounds check */
    printf("Hello, %s! checksum=%d\n", buf, checksum(buf));
}

int main(int argc, char **argv) {
    greet(argc > 1 ? argv[1] : "world");
    return 0;
}

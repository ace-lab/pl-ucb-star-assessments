/* Smoke-test program used by build_and_smoke_test.sh only. Real questions ship
 * their own vuln.c; the page sends it to the workspace, which compiles it. */
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

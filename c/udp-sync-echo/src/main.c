#include <stdio.h>
#include <time.h>

//int clock_getres(clockid_t clk_id, struct timespec *res);

int main() {
    struct timespec ts, tn; // declare struct timespec
    if (0 != clock_getres(_CLOCK_MONOTONIC_RAW, &ts))
        printf("Error, can't get clock precision\n");
    else
        printf("Time resolution: %d ns \n", ts.tv_nsec);

    if (0 != clock_gettime(_CLOCK_MONOTONIC_RAW, &tn))
        printf("Error, can't get clock\n");
    else
        printf("Time is: %d \n", tn.tv_nsec);


    printf("Hello, World!\n");
    return 0;
}
//
// From https://www.tutorialspoint.com/cprogramming/c_pointers.htm
//

#include <stdio.h>

int main () {

    int  var = 20;   /* actual variable declaration */
    int  *ip;        /* pointer variable declaration */

    ip = &var;  /* store address of var in pointer variable*/

    printf("Address of var variable: %x\n", &var  );

    /* address stored in pointer variable */
    printf("Address stored in ip variable: %x\n", ip );

    /* access the value using the pointer */
    printf("Value of *ip variable: %d\n", *ip );


    // Null pointer

    int *ptr = NULL;

    printf("The value of ptr is : %x\n", ptr  );

    int i = 1;
    int *pi = &i;


    // succeeds if p is not null
    if(pi) {
        printf("pointer to i is not null\n");
    }
    // succeeds if p is null
    if(!ptr) {
        printf("ptr is null\n");
    }

    return 0;
}
// wrong_ex3.c - if com ')' faltando
#include <stdio.h>

int main(void) {
    int x = 10;

    if (x > 0 {              // ERRO sintático: faltou ')'
        printf("Positivo\n");
    }

    return 0;
}
// wrong_ex4.c - bloco de função sem '}' final
#include <stdio.h>

int main(void) {
    int x = 0;
    int limit = 3;

    while (x < limit) {
        printf("x = %d\n", x);
        x = x + 1;
    }

    if (x == limit) {
        printf("Terminou o loop\n");
    }

// ERRO sintático: faltou '}' de fechamento da função
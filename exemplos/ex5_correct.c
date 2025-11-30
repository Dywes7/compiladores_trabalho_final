// correct_ex5.c - versão corrigida do wrong_ex5.c
#include <stdio.h>

int main(void) {
    int x = 5;
    int y = 2;

    x = x * y;

    if (x > 0 && y > 0) {
        printf("Ambos positivos\n");
    }

    return 0;
}
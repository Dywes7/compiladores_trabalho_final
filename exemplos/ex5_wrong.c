// wrong_ex5.c - caractere inválido '@' em expressão
#include <stdio.h>

int main(void) {
    int x = 5;
    int y = 2;

    x = x @ y;      // ERRO léxico: caractere inválido '@'
                    // (seu léxico deve reclamar desse símbolo)

    if (x > 0 && y > 0) {
        printf("Ambos positivos\n");
    }

    return 0;
}
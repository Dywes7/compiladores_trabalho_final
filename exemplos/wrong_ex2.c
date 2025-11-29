// wrong_ex2.c - vírgula em número e identificador inválido
#include <stdio.h>

int main(void) {
    float pi = 3,14;   // ERRO léxico: vírgula como separador decimal
    int 2x = 10;       // ERRO léxico: identificador começando com número

    if (2x > 5) {      // vai gerar mais erros sintáticos em cascata
        printf("Maior que 5\n");
    }

    return 0;
}
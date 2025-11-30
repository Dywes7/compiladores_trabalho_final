// wrong_ex1.c - string não terminada
#include <stdio.h>

int main(void) {
    printf("Hello, world!\n");
    char c = 'B';
    int x = 42;
    string s = "teste;      // ERRO: string não terminada
    return 0;
}
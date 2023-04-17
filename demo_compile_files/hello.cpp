#include <cstdio>
#include "hello.hpp"

int main() {
Hello h;
h.hello();
printf("Answer is %d\n", h.answer());
return 0;
}

void Hello::hello() const {
printf("Hello, world\n");
}

int Hello::answer() const {
return 42;
}
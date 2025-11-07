# CLIKE: A C-Like Language Interpreter

CLIKE is a simple interpreter for a C-like programming language, implemented entirely in Python. It is designed to demonstrate key concepts in compiler and interpreter design, including:

* **Lexical Analysis (Lexer)**: Tokenizes the input source code.
* **Parsing (Parser)**: Builds an Abstract Syntax Tree (AST) using recursive descent.
* **Semantic Analysis**: Manages symbol tables to check for type and scope errors.
* **Interpretation (Interpreter)**: Executes the AST using a call stack to manage function calls and runtime execution.

The language supports a familiar C-like syntax, including data types (`int`, `float`, `char`, `string`, `void`), variables with in-line initialization, statically-sized 1D arrays, arithmetic/relational/logical operators, control flow (`if-else`, `while`, `for`), functions with recursion and array parameters, built-in `print`, `#include` for modularity, and single-line comments.

---

## Language Features and Syntax

CLIKE supports a core subset of C-like syntax, designed for simplicity and educational purposes. All programs must be saved with a `.clike` extension and contain an `int main()` function as the entry point. No global variables are allowed; all declarations must be inside functions or the main block.

### 1. **Program Structure**

A program consists of optional `#include` directives, function declarations, and a mandatory `int main()` function.

* `#include` Directive: Imports function declarations from other `.clike` files (only functions are parsed; main or loose statements are ignored).
* Main Function: The entry point is `int main() { ... }`.

```c
// main.clike
#include "utils.clike"

int main() {
    int result = add(5, 3);
    print(result); // Outputs 8
}
```

### 2. **Data Types and Declarations**

Variables must be declared with their type before use. Declarations must be at the top of blocks (e.g., in `main` or functions). Multiple declarations per line are supported, with optional initialization.

* `int`: Signed integers (e.g., `10`, `0`, `-5`).
* `float`: Floating-point numbers (e.g., `3.14`, `0.0`).
* `char`: Single characters (e.g., `'A'`, initialized to `'\0'`).
* `string`: Strings (e.g., `"Hello"`, initialized to `""`).
* `void`: For functions with no return value.

```c
// Variable Declarations
int i;
float f;
char c;
string s;

// Declaration with Initialization
int x = 10;
float pi = 3.14;
string a = "hello";
char b = 'z';

// Multiple declarations
int y = 5, z, w = 100;
```

**Arrays**: One-dimensional, fixed-size arrays (size must be integer literal). Initialized to defaults (e.g., 0 for int).

```c
int my_array[10];
float f_array[5];

my_array[0] = 100;
int val = my_array[0];
print(my_array[1]);
```

### 3. **Operators and Expressions**

* Arithmetic: `+`, `-`, `*`, `/` (always float division, e.g., `5 / 2 = 2.5`).
* Relational: `==`, `!=`, `<`, `>`, `<=`, `>=`.
* Logical: `&&` (AND), `||` (OR).
* Assignment: `=`.
* Unary: `+`, `-` (e.g., `int x = -5;`).

Operator precedence follows C rules (e.g., `*` before `+`).

```c
int sum = 10 + 5 * 2; // 20
float div = 5 / 2;    // 2.5
```

### 4. Control Flow

**If-Else**: Optional `else`.

```c
if (x < 10) {
    print("x is less than 10");
} else {
    print("x is 10 or more");
}
```

**While Loops**:

```c
int i = 0;
while (i < 5) {
    print(i);
    i = i + 1;
}
```

**For Loops**: C-style `(init; condition; post)`, init can declare variables, post can be comma-separated assignments.

```c
for (int i = 0; i < 5; i = i + 1) {
    print(i);
}
```

### 5. Functions

Functions support typed parameters (including arrays as `type arr[]`), recursion, and `return` (optional for `void`).

```c
int add(int a, int b) {
    return a + b;
}

void print_array(float arr[], int size) {
    for (int i = 0; i < size; i = i + 1) {
        print(arr[i]);
    }
}

int main() {
    float vals[3] = {1.0, 2.0, 3.0}; // Note: Initialization lists not supported; assign individually
    print_array(vals, 3);
}
```

### 6. Built-in Functions

* `print(expression)`: Outputs any type to console.

### 7. Preprocessing

* `#include "file.clike"`: Imports functions from another file.

### 8. Comments

Single-line: `// comment`.

---

## Usage and Examples

### Running the Interpreter

Run via command line:

```bash
python src/clike.py [options] <inputfile.clike>
```

Options:

* `--scope`: Print symbol tables during semantic analysis.
* `--stack`: Print call stack during execution (useful for recursion).
* `--debug`: Verbose logs for lexer, parser, interpreter.

### Examples

See `examples/` for basic programs and `tests/` for advanced/edge cases.

1. **Hello World** (`examples/hello.clike`):

   ```c
   int main() {
       print("Hello, CLIKE!");
   }
   ```

   Output: `Hello, CLIKE!`

2. **Factorial Recursion** (`examples/factorial.clike`):

   ```c
   int factorial(int n) {
       if (n <= 1) {
           return 1;
       } else {
           return n * factorial(n - 1);
       }
   }

   int main() {
       print(factorial(5)); // 120
   }
   ```

3. **Arrays and Loops** (`examples/array.clike`):

   ```c
   int main() {
       int arr[3];
       arr[0] = 10; arr[1] = 20; arr[2] = 30;
       int sum = 0;
       for (int i = 0; i < 3; i = i + 1) {
           sum = sum + arr[i];
       }
       print(sum); // 60
   }
   ```

4. **Include Example** (`examples/main.clike` with `utils.clike`):

   `utils.clike`:

   ```c
   int add(int a, int b) {
       return a + b;
   }
   ```

   `main.clike`:

   ```c
   #include "utils.clike"

   int main() {
       print(add(5, 3)); // 8
   }
   ```

For limitations and unsupported features, see `docs/Syntax.md`.

### Test Results

The following shows the terminal output from running the test suite, confirming that all tests pass successfully:

![Result](/tests/results.png)

---

MIT License (see LICENSE). Copyright (c) 2025 Manas.

# CLIKE Syntax Reference

## Introduction

This document provides a comprehensive reference all supported features, their syntax, and a detailed list of features from standard C that are supported as well as not supported in CLIKE, a simple C-like programming language.

### Supported Features

1. **Comments**

    Only single-line comments using // are supported.

    ```c
    // This is a valid comment.
    int x = 10; // This is also valid.

    /*
    This multi-line
    style is NOT supported.
    */
    ```

2. **Data Types**

    Your language supports four primary data types and a `void` type for functions.

    * `int`: A 64-bit signed integer (from Python's `int`).
    * `float`: A 64-bit floating-point number (from Python's `float`).
    * `char`: A single character, initialized to `\0`.
    * `string`: A string of characters, initialized to `""`.
    * `void`: A type used exclusively for function return types.

3. **Variables & Declaration**

    Variables must be declared at the top of a block (like in `main` or at the start of a function). In-line initialization is also supported.

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

    // Multiple declarations per line are supported
    int y = 5, z, w = 100;
    ```

4. **Arrays**

    Only one-dimensional, fixed-size arrays are supported. The size must be an integer literal.

    ```c

    // Array Declaration
    int my_array[10];
    float f_array[5];

    // Array Access (Assignment)
    my_array[0] = 100;
    my_array[1] = 200;

    // Array Access (Reading)
    int val = my_array[0];
    print(my_array[1]);
    ```

5. **Operators**

    The language supports a standard set of arithmetic, relational, logical, and assignment operators.

    Category | Operators | Notes
    --- | --- | ---
    Arithmetic | `+`, `-`, `*`, `/` | `*`: Can be `int* int`, `float * float`, etc. `/`: Always performs float division, even with two integers (e.g., `5 / 2` results in `2.5`).
    Relational | `==`, `!=`, `<`, `>`, `<=`, `>=` | Used for comparisons in `if`, `while`, etc.
    Logical | `&&`, `\|\|` | AND, OR operators
    Assignment | `=` | Assigns a value to a variable or array index.
    Unary | `+`, `-` | e.g., `int x = -5`;

6. **Control Flow**

    Standard `if-else`, `while`, and C-style `for` loops are supported.

    `if-else` Statement
    The `else` block is optional.

    ```c
    if (x < 10) {
        print("x is less than 10");
    } else {
        print("x is 10 or more");
    }

    if (y == 0) {
        print("y is zero");
    }
    ```

    `while` Loop

    ```c
    int i = 0;
    while (i < 5) {
        print(i);
        i = i + 1;
    }
    ```

    `for` Loop
    Supports the C-style `(init; condition; post)` structure.

    * The `init` part can be a declaration (`int i = 0`) or an assignment (`i = 0`).
    * The `post` part can be a single or comma-separated list of assignments.

    ```c
    // Standard 'for' loop
    int j;
    for (j = 0; j < 5; j = j + 1) {
        print(j);
    }

    // 'for' loop with in-loop declaration
    for (int k = 0; k < 3; k = k + 1) {
        print(k);
    }
    ```

7. **Functions**

    You can define and call functions with specified return types and typed parameters.

    ```c

    // Function Declaration
    int add(int a, int b) {
        return a + b;
    }

    void say_hello(string name) {
        print("Hello, ");
        print(name);
        return; // 'return' is optional in void functions
    }

    // Function Call
    int sum = add(5, 3);
    say_hello("Fellow Human");
    ```

8. **Built-in Functions**

    There is one built-in function for console output.

    print(expression): Evaluates the expression and prints its value to the console.

    ```c
    print("Hello World");
    print(10 * 5);
    int x = 10;
    print(x);
    ```

9. **Preprocessing**

    A single preprocessing directive, `#include`, is supported.

    * `# include "filename.c"`: This will parse the specified file before parsing the main file.
    * Limitation: The include-parser only looks for and registers `FunctionDecl` nodes. Any `main` block or loose code in the included file is ignored. This is intended for importing libraries of functions.

### Unsupported Features (Limitations)

This section details common C features that your language does not support.

1. **Comments**

    * **No** `/*...*/` **multi-line comments**.

2. **Data Types & Variables**

    * **No Pointers**: There is no concept of pointers (`int*p;`), addresses (`&x`), or dereferencing (`*p`).
    * **No Global Variables**: All variables must be declared inside the `main` block or another function. You cannot declare a variable in the global scope.
    * **No User-Defined Types**: `struct`, `enum`, `union`, and `typedef` are not supported.
    * **No Type Qualifiers**: `const`, `static`, `volatile`, `unsigned`, `long`, `short`, or `double` are not recognized.
    * **No** `bool` **type**: Use `int` (where `0` is false and non-zero is true).

3. **Arrays**

    * **No Multi-dimensional Arrays**: You cannot declare `int matrix[5][10];`.
    * **No Initialization Lists**: You cannot initialize an array on declaration (e.g., `int a[3] = {1, 2, 3};`). Arrays are always initialized with default values (`0`, `0.0`, `""`, `\0`).
    * **No Dynamic Sizing**: The array size must be a static integer. `int arr[x];` (where `x` is a variable) is not supported.

4. **Operators**

    * **No Integer Division**: The `/` operator always performs float division.
    * **No Modulo Operator**: The `%` operator is not supported.
    * **No Increment/Decrement**: `++` and `--` (both prefix and postfix) are not supported. You must use `i = i + 1`.
    * **No Compound Assignment**: `+=`, `-=`, `*=`, `/=`, `%=` are not supported.
    * **No Bitwise Operators**: `&`, `|`, `^`, `~`, `<<`, `>>` are not supported.
    * **No Ternary Operator**: The `condition ? true_val : false_val` operator is not supported.
    * **No** `sizeof` **operator**.

5. **Control Flow**

    * **No** `switch` **statements**.
    * **No** `do-while` **loops**.
    * **No** `break` **or** `continue`: You cannot break out of a loop early or skip to the next iteration.
    * **No** `goto` **statements**.

6. **Functions**

    * **No Function Prototypes**: You cannot declare a function's "signature" without its body. (The `#include` feature bypasses this by just reading full function definitions from other files).
    * **No Standard Library**: Besides `print`, no other C standard library functions (like `scanf`, `malloc`, `free`, `strcpy`, `printf`) exist.
    * **No Variadic Functions**: Functions must have a fixed number of arguments.
    * **No Function Pointers**.

7. **Preprocessing**

    * **No Macros**: `#define` is not supported.
    * **No Conditional Compilation**: `#ifdef`, `#ifndef`, `#if`, `#endif` are not supported.

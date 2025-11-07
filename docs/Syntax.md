# CLIKE Syntax Reference

## Introduction

This document provides a comprehensive reference to all supported features, their syntax, and a detailed list of features from standard C that are supported as well as not supported in CLIKE, a simple C-like programming language implemented in Python.

### Supported Features

1. **Comments**

    Only single-line comments using // are supported.

    ```clike
    // This is a valid comment.
    int x = 10; // This is also valid.

    /*
    This multi-line
    style is NOT supported.
    */
    ```

2. **Data Types**

    CLIKE supports four primary data types and a `void` type for functions.

    * `int`: A signed integer (from Python's `int`, effectively 64-bit or more).
    * `float`: A floating-point number (from Python's `float`).
    * `char`: A single character, initialized to `'\0'`. Note: No escape sequences (e.g., `\n`, `\0`) are supported in literals; use simple characters like `'A'`.
    * `string`: A string of characters, initialized to `""`. Note: No escape sequences in string literals.
    * `void`: Used exclusively for function return types that return nothing.

    Note: There is no `bool` type; use `int` where 0 is false and non-zero is true.

3. **Variables & Declaration**

    Variables must be declared at the top of a block (e.g., in `main` or functions). In-line initialization is supported. Multiple declarations per line are allowed. Note: While the parser may allow declarations mid-block, it is recommended to place them at the top to adhere to language design.

    ```clike
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

    // Multiple declarations per line
    int y = 5, z, w = 100;
    ```

4. **Arrays**

    Only one-dimensional, fixed-size arrays are supported. The size must be an integer literal. Arrays are initialized to default values (e.g., 0 for int, 0.0 for float, '\0' for char, "" for string).

    ```clike
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

    CLIKE supports a standard set of arithmetic, relational, logical, and assignment operators.

    Category | Operators | Notes
    --- | --- | ---
    Arithmetic | `+`, `-`, `*`, `/` | `*`: Supports int*int, float*float, etc. `/`: Always performs float division (e.g., `5 / 2` = 2.5).
    Relational | `==`, `!=`, `<`, `>`, `<=`, `>=` | For comparisons in conditions.
    Logical | &&, &#124;&#124; | AND, OR.
    Assignment | `=` | Assigns to variables or array elements.
    Unary | `+`, `-` | e.g., `int x = -5;`.

6. **Control Flow**

    Supports `if-else`, `while`, and C-style `for` loops.

    **If-Else Statement** (else optional):

    ```clike
    if (x < 10) {
        print("x is less than 10");
    } else {
        print("x is 10 or more");
    }
    ```

    **While Loop**:

    ```clike
    int i = 0;
    while (i < 5) {
        print(i);
        i = i + 1;
    }
    ```

    **For Loop** (C-style; init can declare vars, post can be comma-separated):

    ```clike
    // Standard for loop
    int j;
    for (j = 0; j < 5; j = j + 1) {
        print(j);
    }

    // With in-loop declaration
    for (int k = 0; k < 3; k = k + 1) {
        print(k);
    }
    ```

7. **Functions**

    Define and call functions with return types and typed parameters (arrays as `type arr[]`). Supports recursion. `return` optional for void.

    ```clike
    // Function Declaration
    int add(int a, int b) {
        return a + b;
    }

    void say_hello(string name) {
        print("Hello, ");
        print(name);
        // return; optional
    }

    // Function Call
    int sum = add(5, 3);
    say_hello("User");
    ```

8. **Built-in Functions**

    * `print(expression)`: Prints the evaluated expression (any type) to console.

    ```clike
    print("Hello");
    print(10 * 5);
    print(x);
    ```

9. **Preprocessing**

    Supports `#include "filename.clike"` to import function declarations (ignores main/loose code).

### Unsupported Features (Limitations)

1. **Comments**

    * No `/*...*/` multi-line comments.

2. **Data Types & Variables**

    * No pointers (`*`, `&`).
    * No global variables (all inside functions/main).
    * No user-defined types (`struct`, `enum`, `union`, `typedef`).
    * No qualifiers (`const`, `static`, `volatile`, `unsigned`, etc.).
    * No `bool` type (use `int`).
    * No `double`, `long`, `short`.
    * No escape sequences in char or string literals (e.g., `\n`, `\0`).

3. **Arrays**

    * No multi-dimensional arrays.
    * No initialization lists (e.g., `int a[3] = {1,2,3};`).
    * No dynamic sizing (size must be literal).

4. **Operators**

    * No integer division (always float).
    * No modulo `%`.
    * No `++`, `--`.
    * No compound assignment (`+=`, etc.).
    * No bitwise operators.
    * No ternary `? :`.
    * No `sizeof`.

5. **Control Flow**

    * No `switch`.
    * No `do-while`.
    * No `break`, `continue`.
    * No `goto`.

6. **Functions**

    * No prototypes (full defs only; #include for import).
    * No std lib except `print`.
    * No variadic functions.
    * No function pointers.

7. **Preprocessing**

    * No `#define` macros.
    * No conditional compilation (`#ifdef`, etc.).

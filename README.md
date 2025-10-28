# CLIKE: A C-Like Language Interpreter

CLIKE is a simple interpreter for a C-like programming language, implemented entirely in Python. It is designed to demonstrate key concepts in compiler and interpreter design, including:

* **Lexical Analysis (Lexer)**: Tokenizes the input source code.
* **Parsing (Parser)**: Builds an Abstract Syntax Tree (AST) using recursive descent.
* **Semantic Analysis**: Manages symbol tables to check for type and scope errors.
* **Interpretation (Interpreter)**: Executes the AST using a call stack to manage function calls and runtime execution.

The language supports a familiar C-like syntax, including data types (`int`, `float`, `char`, `string`), `arrays`, conditional statements (`if`/`else`), loops (`for`/`while`), functions, and an `#include` directive for basic modularity.

---

## Language Features and Syntax

CLIKE supports a core subset of C-like syntax, designed for simplicity and educational purposes. All programs must be saved with a `.clike` extension and contain an `int main()` function as the entry point.

### 1. **Program Structure**

A program consists of optional `#include` directives, function declarations, and a mandatory `int main()` function.

* `#include` Directive: Allows importing functions from other `.clike` files. The path is specified as a string literal.
* Main Function: The entry point for execution is `int main() { ... }`.

```c
// main.clike
#include "utils.clike"

int main() {
    int result = add(5, 3);
    print(result); // Outputs 8
}
```

### 2. **Data Types and Declarations**

Variables must be declared with their type before use. CLIKE supports:

* `int`: Integers (e.g., `10`, `0`, `-5`).
* `float`: Floating-point numbers (e.g., `3.14`, `0.0`).
* `char`: Single characters (e.g., `'A'`).
* `string`: String literals (e.g., `"Hello"`).
* `void`: Used as a return type for functions that do not return a value.

**Variable Declaration and Initialization**: Variables can be initialized at declaration.

```c
int x = 10;
float pi = 3.14;
char initial = 'J';
string greeting = "Hello, CLIKE!";
```

**Arrays**: Arrays are declared with a fixed size.

```c
int nums[3];
nums[0] = 10;
nums[1] = 20;
nums[2] = 30;

char letters[2];
```

### 3. **Operators and Expressions**

CLIKE supports standard arithmetic, comparison, and logical operators.

* Arithmetic: `+`, `-`, `*`, `/` (division is float-based).
* Comparison: `==,` `!=`, `<`, `<=,` `>`, `>=`.
* Logical: `&&` (AND), `||` (OR).
* Assignment: `=`.

```c
int sum = 10 + 5;           // 15
float result = (sum * 2.0) / 3.0;

if (sum > 10 && result <= 10.0) {
    print("Condition met");
}
```

### 4. Control Flow

**If-Else Statements**: Used for conditional logic. The `else` block is optional.

```c
if (x > 0) {
    print("Positive");
} else if (x == 0) {
    print("Zero");
} else {
    print("Negative");
}
```

**While Loops**: Executes a block of code as long as a condition is true.

```c
int i = 0;
while (i < 3) {
    print(i);
    i = i + 1;
}
// Outputs: 0, 1, 2
```

**For Loops**: A `for` loop combines initialization, a condition, and a post-loop operation. The initialization part can include a new variable declaration.

```c
int sum = 0;
for (int i = 0; i < 3; i = i + 1) {
    sum = sum + arr[i];
}
```

### 5. Functions

Functions must be declared with a return type, name, and parameters. Arrays can be passed as parameters.

* **Return Type**: `int`, `float`, `char`, `string`, or `void`.
* **Parameters**: Can be scalar types or arrays (e.g., `int arr[]`).
* **Return Statement**: `return` is used to send a value back from a function.

```c
// Function definition
int factorial(int n) {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1); // Recursion is supported
    }
}

// Function with no return value
void print_array(int arr[], int size) {
    for (int i = 0; i < size; i = i + 1) {
        print(arr[i]);
    }
}

// Function call
int main() {
    int f = factorial(5);
    print(f); // Outputs 120
}
```

### 6. Built-in Functions

`print(expression)`: The primary way to output values to the console. It can print any data type.

### 7. Comments

Single-line comments are supported using `//`.

```c
// This is a single-line comment.
int x = 1; // This comment is at the end of a line.
```

---

## Usage and Examples

### How to Run the Interpreter

The CLIKE interpreter is run from the command line using Python. You must provide a .clike source file as an argument. The interpreter will then lex, parse, analyze, and execute the code.

**Command:**

```bash
python archieve/c-like.py [options] <inputfile>
```

**Options**: The interpreter provides several flags for debugging:

* `--scope`: Print detailed scope and symbol table information during semantic analysis.
* `--stack`: Print the call stack during runtime for debugging function calls.
* `--debug`: Print verbose, step-by-step logs from the lexer, parser, and interpreter.

**Examples**:

The `examples/` directory contains several programs that demonstrate the language's features.

1. **Hello, CLIKE!**

    This is a basic "Hello, World!" program that demonstrates the print function and string literals.

    **File**: `examples/hello.clike`

    ```c
    // A simple "Hello, CLIKE!" program

    int main() {
        print("Hello, CLIKE!");
    }
    ```

    **To Run**:

    ```bash
    python archieve/c-like.py examples/hello.clike
    ```

    **Output**:

    ```bash
    Hello, CLIKE!
    ```

2. **Factorial (Recursion)**

    This example shows how to define and call a recursive function to compute a factorial.

    **File**: `examples/factorial.clike`

    ```c
    // A program to compute factorial using recursion

    int factorial(int n) {
        if (n <= 1) {
            return 1;
        } else {
            return n * factorial(n - 1);
        }
    }

    int main() {
        int result = factorial(5);
        print(result);
    }
    ```

    **To Run**:

    ```bash
    python archieve/c-like.py examples/factorial.clike
    ```

    **Output**:

    ```bash
    120
    ```

3. **Arrays and Loops**

    This program demonstrates declaring an array, assigning values, and using a for loop to iterate over it.

    **File**: `examples/array.clike`

    ```c
    // A program demonstrating arrays and for loops

    int main() {
        int arr[3];
        arr[0] = 10;
        arr[1] = 20;
        arr[2] = 30;

        int sum = 0;
        for (int i = 0; i < 3; i = i + 1) {
            sum = sum + arr[i];
        }
        print(sum); // Outputs 60
    }
    ```

    **To Run**:

    ```bash
    python archieve/c-like.py examples/array.clike
    ```

    **Output**:

    ```bash
    60
    ```

4. Imports with #include

    This example shows how to use the #include directive to import functions from another file (utils.clike) into the main program (main.clike).

    File: `examples/utils.clike`

    ```c
    // Utility functions for import example

    int add(int a, int b) {
        return a + b;
    }
    ```

    File: `examples/main.clike`

    ```c
    # Program demonstrating import with #include

    #include "utils.clike"

    int main() {
        int result = add(5, 3);
        print(result); // Outputs 8
    }
    ```

    To Run:

    ```bash
    python archieve/c-like.py examples/main.clike
    ```

    Output:

    ```bash
    8
    ```

---

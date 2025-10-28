# High-Level Architecture

"CLIKE" language is implemented using a classic **multi-pass interpreter architecture**. This is a standard and robust design where the source code is processed in several sequential stages (or "passes"). Each stage takes the output from the previous one, transforms it, and feeds it to the next.

The entire execution pipeline can be visualized as:

`Source File (.c)` → Lexer → `Stream of Tokens` → Parser → `Abstract Syntax Tree (AST)` → Semantic Analyzer → `Validated AST` → Interpreter → `Program Output`

Here's a detailed explanation of each component.

## 1. The "CLIKE" Language: Features

First, let's define what your language can do, based on the components you've built:

* **Data Types**: `int`, `float`, `char`, `string`, and `void` for function return types.
* **Variables**: C-style declarations (`int x;`) and in-line initialization (`int y = 10;`).
* **Data Structures**: Statically-sized 1D arrays (e.g., `int my_array[10];`).
* **Operators**:
  * **Arithmetic**: `+`, `-`, `*`, `/` (float division).
  * **Relational**: `==`, `!=`, `<`, `>`, `<=`, `>=`.
  * **Logical**: `&&` (AND), `||` (OR).
* **Control Flow**: `if-else` statements, `while` loops, and `for` loops with C-style `(init; condition; post)` clauses.
* **Functions**:
  * Function declarations with typed parameters (e.g., `int add(int a, int b) { ... }`).
  * `return` statements (with or without a value).
  * Function calls (e.g., `my_func(1, 2)`).
* **Built-in I/O**: A `PRINT(...)` function for outputting values to the console.
* **Preprocessing**: A simple file-inclusion directive: `#include "filename.clike"`.
* **Comments**: Single-line comments using `//`.

## 2. Component Deep-Dive

Here is the breakdown of each class in your pipeline and its role.

### Stage 1: Lexer (Tokenizer)

* **Key Class**: `Lexer`
* **Input**: Raw source code text (a string).
* **Output**: A stream of `Token` objects.

The **Lexer**'s job is to scan the raw text and convert it into a sequence of "tokens." A token is a small, meaningful unit of the language, like a keyword, an operator, or a number.

* It iterates through the text character by character.
* It uses helper methods like `_id()` to group characters into complete "lexemes" (e.g., `while`, `my_var`, `123.45`).
* It skips non-essential code like whitespace and comments (`//`).
* It uses `peek()` to look one character ahead, which is crucial for distinguishing between single-char operators (`=`) and multi-char operators (`==`).
* It identifies keywords (like `if`, `int`) by checking them against the `RESERVED_KEYWORDS` dictionary. If a word isn't a keyword, it's classified as an `ID` (identifier).
* Each token also stores its line and column number, which is essential for providing useful error messages later.

**Example**:

* **Input Text**: `int x = 10;`
* **Output Tokens**: `[Token(INT, 'int'), Token(ID, 'x'), Token(ASSIGN, '='), Token(INTEGER_CONST, 10), Token(SEMI, ';')]`

### Stage 2: Parser (Syntax Analyzer)

* **Key Class**: `Parser`
* **Input**: The stream of `Tokens` from the Lexer.
* **Output**: An **Abstract Syntax Tree (AST)**.

The **Parser** takes the flat list of tokens and builds a hierarchical tree structure that represents the program's grammar and logical structure. This tree is the **AST**. You have defined many `AST` node classes (like `BinOp`, `If`, `While`, `FunctionDecl`) to represent each part of your language.

* **Method**: You've implemented a Recursive Descent Parser. This is a common technique where each "rule" of your grammar (like `statement`, `expr`, `term`) is a method in the `Parser` class.
* **Grammar Rules**: The methods define the language's "grammar." For example, the `term` method knows that a term is a `factor` followed by any number of `*` or `/` operations. This creates the correct operator precedence (multiplication before addition).
* `eat(token_type)`: This is the core helper function. It asserts that the `current_token` is what is expected (e.g., a `LPAREN`) and then "eats" it by advancing to the next token.

**Special Feature: `#include` Handling**

Your parser's `parse_includes` method is a key architectural feature. When it encounters `#include "filename.c"`:

1. It pauses parsing the current file.
2. It creates a new Lexer and a new Parser for the included file (`filename.c`).
3. It then only parses the function declarations (`function_decl`) from that file.
4. It adds these functions to the main `Program` node's list of functions.
5. Any `main` block or loose statements in the included file are ignored. This is a smart way to implement header-like functionality.

### Stage 3: Semantic Analyzer

* **Key Class**: `SemanticAnalyzer`
* **Input**: The AST from the Parser.
* **Output**: A validated AST (or a `SemanticError`).

The AST from the parser is syntactically correct (the grammar is right), but it might not be logically correct. The Semantic Analyzer walks the AST (using the `NodeVisitor` pattern) to check for these "meaning" errors.

* **Key Data Structure**: `ScopedSymbolTable`. This is the "brain" of this stage.
* **Symbol Table**: This data structure tracks every variable and function you declare.
* **Scoping**: When the analyzer enters a function (`visit_FunctionDecl`), it creates a **new scope** that is "enclosed" by the previous scope (e.g., the global scope).
* **Lookup**: When it checks a variable (`visit_Var`), it first looks in the current scope. If it's not found, it checks the enclosing scope, and so on, up to the global scope.

This component is responsible for catching errors like:

* `ID_NOT_FOUND`: Using a variable that was never declared (e.g., `x = 5`; without `int x;`).
* `ARG_COUNT_MISMATCH`: Calling a function with the wrong number of arguments.
* **Basic Type Errors**: You've implemented one check in `visit_Assign` to prevent assigning a `float` value to an `int` variable.

### Stage 4: Interpreter (Executor)

* **Key Class**: `Interpreter`
* **Input**: The validated AST.
* **Output**: The program's runtime behavior (e.g., console output).

This is the final stage that "runs" your code. The **Interpreter** walks the AST one last time (again, as a `NodeVisitor`) and executes the logic for each node.

* **Key Data Structures**: CallStack and ActivationRecord.
* `ActivationRecord` **(AR)**: This is the runtime equivalent of a ScopedSymbolTable. It's a simple dictionary (members) that maps variable names (strings) to their actual runtime values (e.g., the number 10, the string "hello", or the list [1, 2, 3]).
* `CallStack`: This is a stack (list) of ActivationRecords. It manages the program's memory.

  * When the program starts, the `global` AR is pushed onto the stack.
  * When a function is called, a **new AR** is created for that function's local variables and pushed onto the stack.
  * When a function returns, its AR is **popped** from the stack, and all its local variables are destroyed.

### **The Execution Flow (The "Magic")**

1. `visit_Program`: Pushes the `global` AR onto the `CallStack` and stores all `FunctionDecl` nodes in it so they can be called later.
2. `visit_VarDecl` / `visit_ArrayDecl`: Adds a new entry to the current AR (the one on top of the stack) with a default value (e.g., `var_name: 0` or `array_name: [0, 0, 0]`).
3. `visit_Assign`: Evaluates the right-hand side (`self.visit(node.right)`) to get a value, then stores that value in the current AR (e.g., `ar.members[var_name] = value`).
4. `visit_Var`: Looks up the variable's name in the current AR and returns its value.
5. `visit_BinOp`: Recursively calls `visit` on its left and right children to get their values (e.g., `5` and `3`) and then performs the actual operation (e.g., `5 + 3`) and returns the result (`8`).
6. `visit_If`: Evaluates the `condition` node. If the result is `True`, it calls visit on the `true_branch`. Otherwise, it calls visit on the `false_branch` (if it exists).
7. `visit_FunctionCall`:

    * Looks up the `FunctionDecl` object from the global AR.
    * Creates a new `ActivationRecord` for the function call.
    * Evaluates each argument in the call and stores the values in the new AR (this is parameter passing).
    * Pushes this new AR onto the `CallStack`.
    * Calls `self.visit(func_decl.body)` to execute the function's code.
    * After the body is finished, it pops the AR from the `CallStack`.

8. `visit_Return`: This is a very clever implementation.

    * It evaluates the expression to be returned.
    * It then raises a special `ReturnException` containing that value.
    * This exception immediately stops the execution of the function's body.
    * The `visit_FunctionCall` method has a `try...except ReturnException` block that "catches" this exception, retrieves the value, and returns it as the result of the function call. This is a clean way to implement a "jump" out of a function.

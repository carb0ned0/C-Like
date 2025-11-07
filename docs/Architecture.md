# High-Level Architecture

The CLIKE language is implemented using a classic **multi-pass interpreter architecture**. This is a standard and robust design where the source code is processed in several sequential stages (or "passes"). Each stage takes the output from the previous one, transforms it, and feeds it to the next.

The entire execution pipeline can be visualized as:

`Source File (.clike)` → Lexer → `Stream of Tokens` → Parser → `Abstract Syntax Tree (AST)` → Semantic Analyzer → `Validated AST` → Interpreter → `Program Output`

Here's a detailed explanation of each component.

## 1. The CLIKE Language: Features

CLIKE supports the following features:

* **Data Types**: `int`, `float`, `char`, `string`, and `void` for function return types.
* **Variables**: C-style declarations (`int x;`) and in-line initialization (`int y = 10;`).
* **Data Structures**: Statically-sized 1D arrays (e.g., `int my_array[10];`).
* **Operators**:
  * **Arithmetic**: `+`, `-`, `*`, `/` (float division).
  * **Relational**: `==`, `!=`, `<`, `>`, `<=`, `>=`.
  * **Logical**: `&&` (AND), `||` (OR).
* **Control Flow**: `if-else` statements, `while` loops, and `for` loops with C-style `(init; condition; post)` clauses.
* **Functions**:
  * Function declarations with typed parameters (e.g., `int add(int a, int b) { ... }`), including array parameters (e.g., `int arr[]`).
  * `return` statements (with or without a value; optional for `void`).
  * Function calls (e.g., `my_func(1, 2)`), with support for recursion.
* **Built-in I/O**: A `print(...)` function for outputting values to the console (supports any type).
* **Preprocessing**: A simple file-inclusion directive: `#include "filename.clike"`.
* **Comments**: Single-line comments using `//`.

For a full syntax reference and limitations, see `docs/Syntax.md`.

## 2. Component Deep-Dive

Here is the breakdown of each class in the pipeline and its role.

### Stage 1: Lexer (Tokenizer)

* **Key Class**: `Lexer`
* **Input**: Raw source code text (a string).
* **Output**: A stream of `Token` objects.

The **Lexer** scans the raw text and converts it into a sequence of "tokens." A token is a small, meaningful unit of the language, like a keyword, an operator, or a number.

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

The **Parser** takes the flat list of tokens and builds a hierarchical tree structure that represents the program's grammar and logical structure. This tree is the **AST**. Many `AST` node classes (like `BinOp`, `If`, `While`, `FunctionDecl`) represent each part of the language.

* **Method**: Recursive Descent Parser, where each grammar rule (like `statement`, `expr`, `term`) is a method in the `Parser` class.
* **Grammar Rules**: The methods define the language's "grammar." For example, the `term` method handles factors followed by `*` or `/` operations, enforcing operator precedence.
* `eat(token_type)`: Asserts the current token matches the expected type and advances to the next.

**Special Feature: `#include` Handling**

The `parse_includes` method handles `#include "filename.clike"`:

1. Pauses parsing the current file.
2. Creates a new Lexer and Parser for the included file.
3. Parses only function declarations (`function_decl`) from the included file.
4. Adds these functions to the main `Program` node's list of functions.
5. Ignores any `main` block or loose statements in the included file, enabling header-like functionality.
6. Supports relative paths and prevents recursive includes.

The parser also handles debugging logs if `--debug` is enabled, printing parsing steps.

### Stage 3: Semantic Analyzer

* **Key Class**: `SemanticAnalyzer`
* **Input**: The AST from the Parser.
* **Output**: A validated AST (or a `SemanticError`).

The Semantic Analyzer walks the AST (using the `NodeVisitor` pattern) to check for semantic errors.

* **Key Data Structure**: `ScopedSymbolTable`.
* **Symbol Table**: Tracks variables and functions with their types and scopes.
* **Scoping**: Creates a new scope for each function (`visit_FunctionDecl`), enclosed by the parent scope (e.g., global).
* **Lookup**: Resolves symbols starting from the current scope, falling back to enclosing scopes.

Errors caught include:

* `ID_NOT_FOUND`: Undeclared variable usage.
* `ARG_COUNT_MISMATCH`: Wrong number of function arguments.
* Basic type checks: e.g., prevents assigning `float` to `int`.

If `--scope` is enabled, it logs symbol tables for each scope (global and functions) after analysis.

### Stage 4: Interpreter (Executor)

* **Key Class**: `Interpreter`
* **Input**: The validated AST.
* **Output**: Program runtime behavior (e.g., console output).

The **Interpreter** walks the AST (as a `NodeVisitor`) and executes each node.

* **Key Data Structures**: `CallStack` and `ActivationRecord`.
* `ActivationRecord` **(AR)**: Runtime scope; a dictionary mapping names to values (e.g., numbers, strings, lists for arrays).
* `CallStack`: Stack of ARs for managing memory and function calls.
  * Global AR pushed at start.
  * New AR for each function call, popped on return.

Execution handles:

* Variable/array declarations with defaults.
* Assignments, including array access with bounds checks.
* Binary/unary operations.
* Control flow (if, while, for).
* Function calls with parameter passing and recursion.
* `return` via `ReturnException` for clean jumps.
* `print` for output.

If `--stack` is enabled, it logs the call stack on entering/leaving program and functions, showing AR contents.

If `--debug` is enabled, it prints detailed execution steps (e.g., declarations, assignments, function calls, exceptions).

## 3. Debugging and Logging

CLIKE includes command-line flags for debugging:

* `--debug`: Verbose logs during parsing and interpretation (e.g., node visits, assignments).
* `--scope`: Prints symbol tables after semantic analysis.
* `--stack`: Prints call stack snapshots during execution, useful for tracing recursion and scope.

These features aid in understanding the interpreter's internal state without altering core execution.

# 🎓 Instructor's Guide: Creating Engaging Tutorials

Welcome to the Checkpoint Instructor's Guide! This document will walk you through the process of creating engaging, interactive tutorials that students will love. We'll show you how to transform traditional assignments into exciting mission-based learning experiences.

## 📚 Table of Contents
- [Understanding the Challenge](#understanding-the-challenge)
- [The Checkpoint Advantage](#the-checkpoint-advantage)
- [Creating Your First Tutorial](#creating-your-first-tutorial)
- [Advanced Pattern Matching](#advanced-pattern-matching)
- [Future Features & Collaboration](#future-features--collaboration)

## 🤔 Understanding the Challenge

Let's look at a real-world example. Suppose you're teaching a course like Berkeley's CS61C, and you have a [GDB debugging assignment](https://cs61c.org/fa24/labs/lab02/#exercise-2-intro-to-gdb) that looks like this:

> You should be filling in `ex2_commands.txt` with the corresponding commands. Please only use the commands from the table above. For correctness, we will be checking the output of your `ex2_commands.txt` against a desired output. We'd recommend opening two SSH windows so you can have the commands file and the cgdb session at the same time.
> 
> [... setup instructions omitted ...]
> 
> For each of the following steps, add the CGDB commands you execute to `ex2_commands.txt`. Each command should be on its own line. Each step below will require one or more CGDB commands.
> 1. Start your program so that it's at the first line in main, using one command.
>
> [... more steps omitted ...]
>
> 9. Step to the last line of the function.
>
> [... remaining steps omitted ...]

This approach can be frustrating for both students and instructors. Students don't get immediate feedback, and instructors have to write rigid checkers that might reject valid solutions. The lack of immediate feedback means students might spend hours debugging their command file rather than learning debugging skills.

## ✨ The Checkpoint Advantage

Checkpoint transforms this experience into an interactive journey! Students no longer need to write commands in a separate file - instead, they work directly in a terminal environment with instant feedback. Every successful command brings immediate validation, complete with visual celebrations and achievement flags. The entire learning process becomes an exciting exploration, where students can focus on learning debugging skills rather than managing command files.

## 🧑‍🏫 Creating Your First Tutorial

Let's transform the GDB assignment into a Checkpoint tutorial! Here's the step-by-step process:

### 🔧 Set Up the Environment

First, let's prepare the GDB environment just like in the original CS61C lab. Navigate to the template workspace:

```bash
cd examples/questions/gdb-tutorial/workspaceTemplate
```

Compile the source files with debugging symbols:
```bash
gcc -g -o pwd_checker test_pwd_checker.c pwd_checker.c
```

Now we have a debuggable program ready for our tutorial. Let's design the missions that will guide students through the debugging process.

### 🎯 Example: Starting the Program

Now comes the fun part - transforming traditional debugging steps into interactive missions! Let's create our first one: getting students to start the program and stop at main. To design this mission, let's first try the command ourselves and see what output we need to validate:

```bash
(gdb) start
Temporary breakpoint 1 at 0x11b8: file test_pwd_checker.c, line 6.
Starting program: /home/student/pwd_checker 
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".

Temporary breakpoint 1, main () at test_pwd_checker.c:6
6           printf("Running tests...\n\n");
```

Our first attempt at a regex pattern might be:
```yaml
match: "Temporary breakpoint 1, main () at test_pwd_checker.c:6"
```

But wait! What if a student does this:
```bash
(gdb) b main
Breakpoint 1 at 0x11b8: file test_pwd_checker.c, line 6.
(gdb) run
Starting program: /home/student/pwd_checker 

Breakpoint 1, main () at test_pwd_checker.c:6
6           printf("Running tests...\n\n");
```

Ah! We need to be more flexible. The breakpoint number might be different, and students might use different commands to reach main. Let's focus on what really matters - we're at main, on line 6, about to execute the printf:

```yaml
- title: Start Program
  prompt: "Mission 1: Start your program"
  description: |
    Start your program so that it's at the first line in main, using one command.
    The program should stop at the first line of main().
  listener:
    target: output
    type: regex
    match: "main.*test_pwd_checker\\.c:6.*printf\\(\"Running tests"
```

### 🎯 Example: The Return Statement

For our next mission, we want students to step to the return statement in check_length. Let's see what that looks like:

```bash
(gdb) until 25
check_length (password=0x555555556029 "qrtv?,mp!ltrA0b13rab4ham") at pwd_checker.c:25
25          return meets_len_req;
```

Our first instinct might be to just match the return statement:
```yaml
match: "return meets_len_req;"
```

But look what happens when a student does this:
```bash
(gdb) list 25
20
21      /* Returns true if the length of PASSWORD is at least 10, false otherwise */
22      bool check_length(const char *password) {
23          int length = strlen(password);
24          bool meets_len_req = (length >= 10);
25          return meets_len_req;
26      }
27
```

They can see the line without actually stepping to it! We need to ensure they're actually at that point in the execution:

```yaml
- title: Examine Return
  prompt: "Mission 9: Step to last line"
  description: |
    Step to the last line of the function to examine the return value.
  listener:
    target: output
    type: regex
    match: "check_length.*pwd_checker\\.c:25.*25\\s+return meets_len_req;"
```

However, we discovered another edge case: when students use `next` commands to reach the return statement, they might not see the `check_length` function context in the output. After consulting with ChatGPT, we arrived at a more robust solution that specifically excludes the `list` command output while matching the actual execution point:

```yaml
match: "(?m)(?:^\\s*23\\s+.*$\\n^\\s*24\\s+.*$\\n25\\s+return\\s+meets_len_req;\\s*$)(*SKIP)(*FAIL)|\\s*25\\s+return\\s+meets_len_req;\\s*$"
```

This regex pattern does two clever things:
1. It first identifies and excludes the case where we see three consecutive lines (23, 24, 25) which would appear in a `list` command
2. Then it matches just line 25 with the return statement, which would appear when actually stepping to that line during execution

### 🔍 Pattern Matching Tips

After these examples, we can extract some key principles:

**Match the Invariant, Ignore the Variable**
- ✅ Matches the essential elements (`main`, file name, line number, code)
- ❌ Ignores variable elements (breakpoint numbers, memory addresses)
- 🎯 Focuses on what **must** be present, not what *might* be present

This flexibility is crucial! Students might:
- Set additional breakpoints
- Have different memory addresses
- Use slightly different commands to achieve the same goal

**Important**: When writing patterns in YAML, remember to properly escape special characters. Backslashes need to be doubled (`\\`), and quotes within strings need to be escaped (`\"`).

We know writing regex patterns can be tricky - feel free to use ChatGPT as your regex-writing companion!😉 And to make sure your patterns work as expected, use our `checkpoint validate` command:

### 🧪 Testing Your Patterns

```bash
$ checkpoint validate 9
Enter output to validate (double empty line to submit, Ctrl+C to exit):
check_length (password=0x555555556029 "qrtv?,mp!ltrA0b13rab4ham") at pwd_checker.c:25
25          return meets_len_req;

✅ Match!
```

This tool helps you verify your patterns against real output, test different variations of valid solutions, and ensure your YAML syntax and escaping is correct.

## 🚀 Future Features & Collaboration

We're excited about making Checkpoint even better! Here's what we're working on:

### 💡 Coming Soon

We're developing several new features to make tutorial creation even easier:

- Our upcoming Python API will provide a more flexible way to define flag settings, moving beyond YAML configuration. For simpler cases, we're introducing fuzzy matching that won't require regex patterns - just provide the commands, and we'll help record and compare the output.
- We're also exploring more sophisticated validation approaches. Instead of relying solely on output logs, we could monitor program state directly. For example, with Git tutorials, we could validate repository status by examining the .git directory or running parallel git status commands.
- Perhaps most exciting is our planned LLM integration. Quick-response language models could validate student outputs and provide natural, contextual feedback. Imagine an AI assistant that not only checks if a solution is correct but also offers helpful hints and explanations!

### 🤝 Get Involved!

If these ideas excite you, we'd love to hear your thoughts! Whether you have specific validation needs or ideas for new features, please open an issue or start a discussion on our GitHub repository. Your real-world teaching experiences can help shape the future of Checkpoint.

## 🎮 Try It Yourself!

Experience the difference firsthand with our [GDB Tutorial](../examples/questions/gdb-tutorial). Watch as students light up when they see instant feedback and celebration animations. Each completed mission brings not just a new flag, but a sense of achievement and progress.

---

<p align="center">
  Ready to transform your assignments into exciting learning adventures? 
  Let's make it happen! 🚀
</p>
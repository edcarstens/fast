# FAST (Features And Sections Templater)

FAST is a powerful templater that turns your template
into executable Python code and executes it. To run:

    python fast.py <template file>

## Templating Procedure

(1) Copy your target text file to < filename >.fast

(2) Replace any '\@' characters with '\@\@'

(3) If there are any lines matching the
    Python code syntax (i.e. starting with
    '///' or '//.'), these can be fixed with
    variable substitutions as follows:

    @fast.commentString@/ <text>

which will output

    /// <text>

or

    @fast.commentString@. <text>

which will output

    //. <text>

If there are many such cases, consider
using a different comment string with
the -c option or changing the FAST
variables fast.immCodePrefix and/or
fast.codePrefix.

(4) Process the file and make sure it outputs
    exactly the same contents as the original
    target text file.
    
    python fast.py <template file>

(5) Add Python code lines and text lines with
Python expression substitutions where desired.

## Templating Rules

(1) The first line is used for execution
    only. It is discarded during processing.

(2) '/// < codeline >'

Python code line is immediately executed.
Typically, this is used to include another
FAST file with fast.include(< filename >).

(3) '//.  < codeline >'

A line of Python code, < codeline >, is
appended to the program.

Space preceding the '//.' indicates output
indention. Typically, this feature is used
when calling a function or class method to
output a section of text all with the same
indention.

There are some special cases for which the
space preceding the '//.' is ignored:

 (a) < codeline > ends with ':{'
     This starts a code block.
     The '{' character is not part of
     the generated code.
     
 (b) < codeline > = '{'
     This also starts a code block. No
     code is generated for this line.

 (c) < codeline > = '}'
     This ends a code block. No code
     is generated for this line.

Within a code block explicitly bracketed by
'{' and '}', the space between '//.' and
< codeline > is ignored. FAST takes care of
the code block indention when Python code
is generated.

Outside of bracketed code blocks, this space
is regarded as Python code indention.
Specifying Python code indention is strongly
discouraged. Just let FAST take care of it
for you (i.e. always use '{' and '}').

(4) '< textline >'

A print() call is appended to the program
with a processed < textline > to enable
substitution of Python expressions. This is
useful when text is to be echoed as is or
with some substitutions. If this line is
within a code block, that code block must
be explicitly bracketed by '{' and '}', so
that FAST can insert the proper code
indention.

Note: Python expressions within two '@' characters
in < textline > will be evaluated (to a string)
and inserted into the template text line.
'@@' can be used to escape a '@' character.

For info on the available builtin FAST methods,
use the -i option:

    python fast -i all /dev/null

or

    python fast my.fast -i all

Then for help on a specific FAST method such
as __pos__:

    python fast -i fast.__pos__ /dev/null

or

    python fast my.fast -i fast.__pos__

# FAST Built-in Class Objects and Methods

There are a number of built-in methods available.

## doc
//.fast.includeSection('info:doc')
## info
//.fast.includeSection('info:info')
## fast
//.fast.includeSection('info:fast')
## fast.\_\_getitem\_\_
//.fast.includeSection('info:fast.__getitem__')
## fast.\_\_lshift\_\_
//.fast.includeSection('info:fast.__lshift__')
## fast.\_\_lt\_\_
//.fast.includeSection('info:fast.__lt__')
## fast.\_\_neg\_\_
//.fast.includeSection('info:fast.__neg__')
## fast.\_\_pos\_\_
//.fast.includeSection('info:fast.__pos__')
## fast.\_\_rshift\_\_
//.fast.includeSection('info:fast.__rshift__')
## fast.dedentSection
//.fast.includeSection('info:fast.dedentSection')
## fast.escapeSubChars
//.fast.includeSection('info:fast.escapeSubChars')
## fast.getLines
//.fast.includeSection('info:fast.getLines')
## fast.getSection
//.fast.includeSection('info:fast.getSection')
## fast.include
//.fast.includeSection('info:fast.include')
## fast.includeSection
//.fast.includeSection('info:fast.includeSection')
## fast.off
//.fast.includeSection('info:fast.off')
## fast.on
//.fast.includeSection('info:fast.on')
## fast.printSection
//.fast.includeSection('info:fast.printSection')
## fast.printWithIndent
//.fast.includeSection('info:fast.printWithIndent')
## fast.readFile
//.fast.includeSection('info:fast.readFile')
## fast.removeLastChar
//.fast.includeSection('info:fast.removeLastChar')
## fast.seal
//.fast.includeSection('info:fast.seal')
## fast.soff
//.fast.includeSection('info:fast.soff')
## fast.son
//.fast.includeSection('info:fast.son')
## fast.subChar
//.fast.includeSection('info:fast.subChar')
## fast.subChar1
//.fast.includeSection('info:fast.subChar1')
## fast.subChar2
//.fast.includeSection('info:fast.subChar2')
## fast.unseal
//.fast.includeSection('info:fast.unseal')
## fast.writeFile
//.fast.includeSection('info:fast.writeFile')
## fast.setSection
//.fast.includeSection('info:fast.setSection')

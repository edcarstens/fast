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

    @fast.commentString@/ -text-

which will output

    /// -text-

or

    @fast.commentString@. -text-

which will output

    //. -text-

If there are many such cases, consider
using a different comment string with
the -c option or changing the FAST
variables fast.immCodePrefix and/or
fast.codePrefix.

(4) Process the file and make sure it outputs
    exactly the same contents as the original
    target text file.
    
    python fast.py <template file>

(7) Add Python code lines and text lines with
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

    fast.py -i all /dev/null

or

    my.fast -i all

Then for help on a specific FAST method:

    fast.py -i fast.push /dev/null

or

    my.fast -i fast.push

# FAST Built-in Class Objects and Methods

There are a number of built-in methods available.

## doc
special object used for custom documentation

The example below creates a doc section called
'topic' consisting of the header, '# topic' and
the line,
'Full documentation about topic  here..',
which ordinarily would be many lines of
documentation pertaining to 'topic'. The contents
of this doc section could be written to disk as a
markdown file (doc.md) by calling doc.write(). A
doc section is used for information that is too
detailed to go in a quick reference, for which
an info section should be used. More lengthy and
detailed documentation can go into the doc section.
In your FAST package, you should always write a doc
section first if only to add a proper markdown
header such as '# topic' in the example.

Example

    //.+doc < 'topic'
    # topic
    
    Full documentation about topic here..
    //.-doc

See 'info'

## info
special object used for adding custom info

The example below creates an info section called
'topic' which consists of a one-liner description,
'Brief one-liner description' followed by the full
description. The contents of this info section would
be dumped if the FAST template were called with the
option -i 'topic'. It is recommended you provide
this info for your custom FAST packages/methods for the
benefit of other users. This info can be added
right before each method (def) in a class.

Example

    //.+info < 'topic'
    Brief one-liner description
    More detailed description with examples..
    //.-info
    
Info sections also get added to the doc section.

See 'doc'

## fast
fast([cs]) prints file generation info including a timestamp

cs - comment prefix string (default: '//')

Typically this is placed somewhere in the header.

## fast.\_\_getitem\_\_
\_\_getitem\_\_(x) or fast[x] returns the Section object from fast.sections dict

This is provided as a convenient shortcut for
retrieving the Section object from the fast.sections
dict (i.e. fast.sections[section])

Example

    //.abc = fast['abc']
    
## fast.\_\_lshift\_\_
\_\_lshift\_\_(n) fast<<n decreases output indent by n spaces
## fast.\_\_lt\_\_
\_\_lt\_\_(x) fast<x sets current section (fast.section) to x

A typical usage is shown in the example below. The unary
operator, '+', pushes current context prior to setting
the current section to 'abc', which is done by the '<'
operator. Subsequent lines go into section 'abc'. The
unary operator, '-', pops the previously pushed context.

Example

    //.+fast < 'abc'
    This line is added to section abc
    //.-fast
    
## fast.\_\_neg\_\_
\_\_neg\_\_() -fast pops (fast.indent,fast.enable,fast.section) from stack

The unary operator, '-', pops the context previously
pushed by the unary operator, '+'. In this case, the '<'
operator is setting the current section (fast.section)
to 'abc'. The pop restores the current section. Every
pop must be paired with a previous push.

Example

    //.+fast < 'abc'
    This line is added to section abc
    //.-fast

If the current section before the pop (-fast) is a
file section (i.e. has the prefix 'file:') then the
current section is written to disk as indicated by
its file section name.

Example

    //.+fast < 'file:abc.txt'
    This line is added to file section abc.txt
    //.-fast

The prefix, 'file:', is included in the section name,
but not the filename. The method, fast.writeFile is
called. If sections are sealed, the file section is
unsealed prior to being written to disk.

For more info, see writeFile, seal, and unseal

## fast.\_\_pos\_\_
\_\_pos\_\_() +fast pushes (fast.section,fast.enable,fast.indent) onto stack

The unary operator, '+', pushes the context to the stack
and turns off standard output. (It does not turn off
writing to sections.) Also, fast.section and fast.indent
both get reset to ''

It is commonly chained with the '<' operator, which sets
the current section (fast.section), so it is a convenient
way to restore the current section later with a pop.

Example

    //.+fast < 'abc'
    This line is added to section abc
    //.-fast


Another common use is if there are lines you do not
wish to be output anywhere. FAST packages typically
start with +fast and end with -fast because you
generally don't want a package producing output when
it is included.

Example

    //.+fast
    This line does not go anywhere!
    //.-fast
    
Don't forget the pop (-fast)! Forgetting this can result
in confusing errors making debugging it quite difficult.

## fast.\_\_rshift\_\_
\_\_rshift\_\_(n) fast>>n increases output indent by n spaces
## fast.dedentSection
dedentSection(x) dedents section x

x - name of section to be dedented (string type)

The '<=' operator is a shortcut for dedentSeetion.

Example

    //.fast <= 'abc'

This gets rid of whatever indention the entire
contents of section 'abc' has.

FAST takes care of this automatically if you call
printSection() with an indention specified.

Example

    |123456
    |     //.fast > 'abc'

In this example, section 'abc' will be printed
with precisely 5 spaces of indention, regardless
of its previous indention, because 'abc' is
dedented automatically first. (The '1' represents
column 1, which has no indention.)

## fast.escapeSubChars
escapeSubChars(s) escapes substitution characters
## fast.include
include(fn, [skipFirstLines]) includes FAST file
## fast.includeSection
includeSection(x) includes section x
## fast.off
off() disables FAST output
## fast.on
on() enables FAST output
## fast.printSection
printSection(x) prints contents of section x to current section
## fast.printWithIndent
printWithIndent(s) print string s to current section
## fast.readFile
readFile(fn, [cs]) read file, strip blank lines and comments, return list of lines

fn - filename
cs - comment string (default: //)

## fast.removeLastChar
removeLastChar(x,[c],[cs]) remove last character (c) in section x

## fast.seal
seal() seals all sections
## fast.soff
soff(x) disables writing to section x
## fast.son
son(x) enables writing to section x
## fast.subChar
subChar([s]) substitution character (two usages)
## fast.subChar1
subChar1([s]) left substitution character (two usages)
## fast.subChar2
subChar2([s]) right substitution character (two usages)
## fast.unseal
unseal() useals all sections
## fast.writeFile
writeFile(sfn, fn, [chompMe], [c], [cs]) writes section sfn to disk as fn

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
\_\_lshift\_\_(n) or fast<<n decreases output indent by n spaces
## fast.\_\_lt\_\_
\_\_lt\_\_(x) or fast<x sets current section (fast.section) to x

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
\_\_neg\_\_() or -fast pops (fast.indent,fast.enable,fast.section) from stack

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
file section (i.e. has attribute fn) then the
current section is written to disk using the
specified file name ('abc.txt').

Example

    //.+fast < 'abc.txt'
    //.fast.setFileName()
    This line is added to file section abc.txt
    //.-fast

The setFileName method defaults to using the section name
as the filename if no argument is given. The method,
fast.writeFile is called. If sections are sealed, the file
section is unsealed prior to the write.

For more info, see writeFile, seal, and unseal

## fast.\_\_pos\_\_
\_\_pos\_\_() or +fast pushes (fast.section,fast.enable,fast.indent) onto stack

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
\_\_rshift\_\_(n) or fast>>n increases output indent by n spaces
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

s - string to be escaped

Sections must be sealed when calling this method.
The returned string escapes the substitution
characters so that it yields the desired string
when processed.

Example

    emailAddr = 'joe@foo.net'
    emailAddrEsc = fast.escapeSubChars(emailAddr)

## fast.getLines
getLines(x) returns list of lines of section x
## fast.getSection
getSection(x) gets text (contents) of section x
## fast.include
include(fn, [skipFirstLines]) includes FAST file

fn             - filename of FAST file to load
skipFirstLines - number of header lines to skip

Note: Unlike other methods, this must be called
      immediately during parsing, so be sure to
      use the line prefix, '///'.
      
## fast.includeSection
includeSection(x) includes section x

This method is usually not called directly.
When the '>' operator is used, this method is called
if sections are unsealed (i.e. fast.sealIncludeSection
is False) or you are writing to stdout rather than
into a section, otherwise it outputs a placeholder
line of code to call this method whenever it is
unsealed.

Example

    +fast < 'xyz' ## write into section xyz
    fast.seal()
    fast > 'abc'  ## sealed
    fast.unseal()
    fast > 'abc'  ## unsealed
    -fast

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
## fast.setSection
setSection(x, text) sets text of section x
# Section

The class, 'Section', an extension of SectionBase class,
is useful for creating a hierarchy of named subsections as
well as binding a section to an object name. This simplifies
code because you no longer need to reference the section by
fast.sections[<section name>].

It can be extended and the methods process or processFinal
can be implemented in your extended class to perform input
processing. The process method is called by __neg__. Use
this for more immediate processing of blocks of lines.
The processFinal method is called once just before the
section or any of its subsections is output.

## Section.process
process() user-implemented method called by Section.\_\_neg\_\_

In the Section or SectionBase classes, this method exists
but is not implemented (does nothing). To implement this
method, make a new class extended from Section.

Example

    //.class MyReadData(Section):{
    //.  def __init__(self):{
    //.    self.data = []
    //.    super(MyReadData, self).__init__()
    //.  }
    //.  def process:{
    //.    for line in self.getLines():{
    //.      self.data.append(line.split(','))
    //.    }
    //.  }
    //.}
    //.myReadData = +MyReadData()
    7,5,3,1
    7,6,7,9
    //.-myReadData

## Section.processFinal
processFinal() user-implemented method called by Section.\_\_gt\_\_

In the Section or SectionBase classes, this method exists
but is not implemented (does nothing). This method is only
called once at the first call to Section.\_\_gt\_\_ (Section > x)
where x is the subsection name or empty string for the section
itself.

## Section.\_\_init\_\_
\_\_init\_\_([x],[parent]) initialization of a new Section object

x      - section name (string type)
parent - parent Section object

A new Section object is created with section name, x, if
specified, otherwise a unique section name is automatically
assigned. If the new Section object is a subsection, the
parent argument can be used to point to its parent Section
object.

Example

    apple = Section('apple')
    apple.sub1

This example shows how a new Section object, apple, is
created. Because the next line references a non-existent
object attribute (sub1), the method Section.\_\_getattr\_\_
is called and a new Section object named "apple sub1"
is created whose parent is apple. The object attribute,
sub1, is created to point to the new subsection object.

The recommended naming convention for section names is
similar to Python variable names. The name should start
with a lowercase letter (a-z) and use underscores for
readability or camelCase style if preferred. 

Spaces should never be used because they have special
meaning as they are used as a delimiter for subsection
names (i.e. "apple sub1"). The colon (:) also should
not be used in the name as it is used to indicate info and
doc sections (i.e. "info:fast.on" or "doc:FAST").

## Section.\_\_call\_\_
\_\_call\_\_([fn]) sets the filename, flagging section is a file section

fn - filename

Sets the filename to indicate the section is to be written
to a file with filename fn. If the fn argument is not
provided, the filename defaults to the section name.
The file is written by the Section.write method, which
is called by fast.writeFiles, typically the final method
called from the main FAST template file.

## Section.\_\_iadd\_\_
\_\_iadd\_\_(s) adds line of text, s, to section's text

s - line of text (String type)

The conventional way of adding a line of text to a section
is via templating:

    //.+apple
    Add this line to apple section.
    //.-apple

This method can be called to add a line of text to the
section (apple) in a more straightforward manner.

    //.apple += 'Add this line to apple section.'
    
## Section.\_\_pos\_\_
\_\_pos\_\_() +Section does a push and sets this section as the current fast section

Example

    //.+apple
    Add this line to apple section.
    //.-apple

In this example, the current fast section is set to apple
so that lines between +apple and -apple are added to the
apple section text. The first line (+apple) is equivalent to:

    //.+fast < apple.section

## Section.\_\_getattr\_\_
\_\_getattr\_\_(x) Section.x creates subsection object if x is not already an attribute

x - subsection and attribute name

Example

    //.apple.sub1

In this example, apple is a Section object and 'sub1' is
not already an attribute of apple. When 'sub1' is
referenced, apple.\_\_getattr\_\_ is called with 'sub1'. A
new Section object is created as a subsection with
the name "apple sub1". The attribute 'sub1' of apple now
exists and points to this subsection object. The parent
attribute of apple.sub1 points to apple.

The gory details..
The method, apple.create('apple sub1',apple), is called
to create the subsection. Thus, a class extension may
override the create method so that it uses itself.
Otherwise, the subsection will be a Section object.

## Section.\_\_neg\_\_
\_\_neg\_\_() -Section pops and calls the process method

Example

    //.+apple
    Add this line to apple section.
    Add another line to apple section.
    //.-apple

In the example, -apple, is used at the end of adding
lines to the apple section. This is equivalent to:

    //.-fast
    //.apple.process()

The process method is not implemented by the Section
class. It may be implemented by extending Section.
For more info see Section.process.

## Section.\_\_gt\_\_
\_\_gt\_\_(x) Section > x prints subsection

x - subsection (String type)

Example
    //.+apple
    //.apple > 'sub1'
    //.-apple
    //.apple > ''

The second line prints subsection 'sub1' to the apple
section. More accurately, if sections are sealed, it
places a line of code in the apple section that will
print subsection 'sub1' when executed, which occurs
either when sections are unsealed or the output is to
STDOUT or to a file.

The last line supplies an empty string as an
argument, which tells FAST to print the apple section
itself.

The apple.processFinal method is called at the last
line (apple > '') prior to printing the apple section.
(If sections are sealed, a line of code is inserted
that will call apple.processFinal when executed.)
This method only gets called once. The processFinal
method is not implemented by the Section class. It may
be implemented by extending Section. For more info
see Section.processFinal.

The second line (apple > 'sub1') does not include
a call to apple.sub1.processFinal nor does it call
apple.processFinal. Since subsections should end up
being included in the parent section, it doesn't
make sense they be processed twice.

## Section.write
write([fn]) writes section to a file

fn - filename (String type)


## Section.getText
getText() a getter function that returns the section text
## Section.getLines
getLines() function that returns list of lines of section text
## Section.setText
setText(text) setter function that sets section text

text - lines of text (String type)

## Section.chomp
chomp([c],[cs]) removes last character (c) in section

c  - character to be removed (default: ',')
cs - line comment string (default: '//')

The alias, rstrip, may be used instead of chomp.

Example

    //.apple.chomp > ''

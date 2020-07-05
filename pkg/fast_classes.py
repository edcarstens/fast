from __future__ import print_function
import sys
import os
import re
import argparse
import time
import textwrap
from sect import SectionBase

def setup(fast, installPath, forDebug=False):
    # Argument Parser
    # Workaround for -d option (between fileName and optional positional args)
    debugMode = False
    if ('-d' in sys.argv):
        debugMode = True
        sys.argv.remove('-d')
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description = 'Features And Sections Templater (FAST)',
        epilog = textwrap.dedent('''\
        See complete documentation in pet/doc
        '''))
    parser.add_argument('-i', default='', metavar='<func>',
                    help = 'If <func> = all, report short help info on all existing functions; otherwise, report help info on specified function. These are builtin FAST methods as well as user-defined functions or class methods, called within the FAST file.')
    parser.add_argument('-d', action='store_true',
                    help = 'Debug mode - print generated Python code (fully executable by itself)')
    if (not forDebug):
        parser.add_argument('fileName',
                    help = 'Name of FAST template file to be processed')
    parser.add_argument('args', nargs='*',
                    help = 'Additional arguments passed to your FAST template file in fast.args array')
    args = parser.parse_args()
    fast.debugMode = debugMode
    fast.installPath = installPath
    fast.args = args.args   ## pass additional arguments to fast
    fast.infoFlag = (len(args.i) > 0)
    fast.srcFile = '<debug>' if (forDebug) else args.fileName
    info = InfoClass(fast)  ## for user custom built-in info
    doc = DocClass(fast)    ## for user custom documentation (markdown)
    doc < info              ## any lines written to info also go to doc

    # FAST Info and Documentation (markdown)
    fast.info = InfoClass(fast)
    fast.doc = DocClass(fast)
    fast.doc < fast.info

    # Standard built-in packages
    fast.include('BuiltinHelp.fast')
    fast.include('Section.fast')
    return (info, doc, args)

def process(fast):
    # First pass - generate Python code (fast.srcCode)
    #fast.include(fast.srcFile, 1)  # Ignore first line
    fast.include(fast.srcFile)

    # Second pass -execute Python code
    if (fast.debugMode):
        fast.printCode()
    else:
        fast.printme()

def info(fast, args):
    # Provide info if -i option used
    if (fast.infoFlag):
        if (args.i == 'all'):
            for k in fast.sections:
                if (k[0:5] == 'info:'):
                    fast.getInfoSectionHeader(k)
            fcts = fast.infoDict.keys()
            fcts.sort()
            for k in fcts:
                print(('{:>' + str(fast.maxFctNameLength) + '} - {}').format(k, fast.infoDict[k]))
        else:
            fast.infoFlag = False  ## necessary for printSection to print
            fast.printSection('info:' + args.i)

class ChompClass(object):
    """ chomp class """
    def __init__(self, fast):
        self.fast = fast
        self.c = ','
        self.linecc = '//'
    """ //.fast.chomp(',') """
    def __call__(self, c=',', lineCommentChar='//'):
        self.c = c
        self.linecc = lineCommentChar
        return self
    """ //.fast.chomp < 'section' """
    def __lt__(self, x):
        self.fast.removeLastChar(x, self.c, self.linecc)
    """ //.fast.chomp > 'section' """
    def __gt__(self, x):
        if (self.fast.sealIncludeSection and len(self.fast.section)):
            self.fast.printWithIndent(self.fast.commentString + self.fast.codeChar +
                                     "fast.includeSectionChomp('" + x + "','" +
                                     self.c + "','" + self.linecc + "')")
        else:
            self.fast.includeSectionChomp(x, self.c, self.linecc)
    def printSection(self, x):
        self.fast.removeLastChar(x, self.c, self.linecc).printSection(x)
    """ //.-fast.chomp """
    def __neg__(self):
        #fn = self.fast.getFileName()
        #if (fn):
        #    self.fast.writeFile(self.section, fn, True, self.c, self.linecc)
        self.indent = self.stack.pop()
        self.enable = self.stack.pop()
        self.section = self.stack.pop()
        return self

class InfoClass(object):
    """ info class """
    def __init__(self, _fast, prefix='info:'):
        self.fast = _fast
        self.sectionPrefix = prefix
        self.section = ''
        self.sections = []     # list of all of my sections
        self.infoObjects = []  # list of info class objects
        self.fullSection = ''
    def addInfo(self, x):
        self.infoObjects.append(x)
    def __lt__(self, x):
        if (isinstance(x, InfoClass)):
            x.addInfo(self)
            return x
        else:
            self.sections.append(x)
            self.section = x
            self.fullSection = self.sectionPrefix + self.section
            self.fast < self.fullSection
            return self
    def __pos__(self):
        +self.fast
        return self
    def header(self, x):
        pass
    def process(self, x):
        return x
    def __neg__(self):
        -self.fast
        for i in self.infoObjects:
            +i < self.section
            i.header(self.section)  ## allow for inserting a header
            x = i.process(self.fullSection)
            self.fast.printSection(x)
            -i
        return self
    def __gt__(self, x):
        section = self.sectionPrefix + x
        #self.fast > section
        self.fast.printSection(section)
        #self.fast.includeSection(section)
        return self

class DocClass(InfoClass):
    """ doc class """
    def __init__(self, _fast, prefix='doc:', fn='doc.md'):
        self.fn = fn
        super(DocClass, self).__init__(_fast, prefix)
    def escape(self, s):
        rv = re.sub('\_', "\\_", s)
        return rv
    def header(self, x):
        self.fast >= self.escape('## ' + x)
    def process(self, x):
        text = self.fast.getSection(x)
        ntext = self.escape(text)
        ## Create a new section for ntext
        z = self.fast.createSection()
        self.fast.setSection(z.section, ntext)
        z.isTemporary = True
        return z.section
    def write(self):
        print('DocClass.write')
        +self.fast < self.fn
        self.fast.setFileName(self.fn) # set filename of section
        sections = self.sections
        #sections.sort()
        for x in sections:
            #print('Writing section ' + x)
            self > x
            #self.fast.includeSection(x)
        self.fast.unseal() ## prevent -fast from unsealing
        -self.fast
        self.fast[self.fn].write(self.fn)
        self.fast.seal()
        return self

class FastClass(object):
    """ fast class """
    
    version = '1.0.0'
    newline = '\r\n'

    def subChar(self, x=''):
        if (x):
            self._subChar1 = x
            self._subChar2 = x
            self._initSubVar()
        if (self.sealIncludeSection and self.enableSealedSubstitution):
            return self._subChar1 + 'fast._subChar1' + self._subChar2
        else:
            return self._subChar1
        
    def subChar1(self, x=''):
        if (x):
            self._subChar1 = x
            self._initSubVar()
        if (self.sealIncludeSection and self.enableSealedSubstitution):
            return self._subChar1 + 'fast._subChar1' + self._subChar2
        else:
            return self._subChar1

    def subChar2(self, x=''):
        if (x):
            self._subChar2 = x
            self._initSubVar()
        if (self.sealIncludeSection and self.enableSealedSubstitution):
            return self._subChar1 + 'fast._subChar2' + self._subChar2
        else:
            return self._subChar2
            
    def escapeSubChars(self, s):
        idx1 = s.find(self._subChar1)
        idx2 = s.find(self._subChar2)
        if ((idx2 >= 0) and ((idx2 <= idx1) or (idx1 < 0))):
            return s[:idx2] + self.subChar2() + self.escapeSubChars(s[idx2+1:])
        elif (idx1 >= 0):
            return s[:idx1] + self.subChar1() + self.escapeSubChars(s[idx1+1:])
        return s
        
    def _initSubVar(self):
        self.subVar = re.compile('^(.*?)\\' + self._subChar1 + '(.*?)\\' + self._subChar2 + '(.*)')
        if (self._subChar1 == self._subChar2):
            self.subZeroReplace = self._subChar1         # @@ => @
        else:
            self.subZeroReplace = self._subChar1 + self._subChar2    # {} => {}

    def __init__(self, globalvars):
        self._subChar1 = '@'
        self._subChar2 = '@'
        self.globalvars = globalvars
        self.commentString = '//'
        tmp = '^(\s*)' + self.commentString
        self.immCodePrefix = re.compile('^\s*' + self.commentString + '/(.*)')
        self.codePrefix = re.compile(tmp + '\.(\s*)(.*)')
        self.codeChar = '.'
        self._initSubVar()
        self.chomp = ChompClass(self)
        self.rstrip = self.chomp                         # alias for chomp
        self.srcCode = ''                                # Python code string to be executed
        self.codeIndent = 0                              # absolute indention of the Python code
        self.indent = ''                                 # absolute indention of output text as a string
        self.lastIndent = ''                             # latest relative indention added
        self.section = ''                                # current section name
        self.sections = dict()                           # sections dictionary
        self.stack = []                                  # stack (array)
        self.enable = True                               # output enable
        self.infoFlag = False                            # info flag
        self.maxFctNameLength = 0
        self.infoDict = dict()
        self.srcFile = ''
        self.sectionDisable = dict()
        self.debugPrintExecutable = False
        self.firstLine = ''
        self.sealIncludeSection = True     # includeSection calls are sealed
        self.recursionLimit = 20           # recursion limit on includeSection
        self.includeSectionDepth = 0       # recursion depth counter (nested calls)
        self.enableSealedSubstitution = True
        self.tmpSection = '___Temporary-Section___'  # used only temporarily by FAST methods, then deleted
        self.docUrl = 'doc/fast.md'
        self.line = ''       # current line (string) being parsed
        self.lineNum = 0     # current line number being parsed within main or included file
    def escape(self, s):
        rv = re.sub('\\\\', "\\\\\\\\", s)
        rv = re.sub("'", "\\'", rv)
        return rv
    def text2code(self, line):
        m = re.match(self.subVar, line)
        if (m):
            if len(m.group(2))==0:
                return "'" + self.escape(m.group(1)) + self.subZeroReplace + "'+" + self.text2code(m.group(3))
            else:
                return "'" + self.escape(m.group(1)) + "'+str(" + m.group(2) + ")+" + self.text2code(m.group(3))
        else:
            return "'" + self.escape(line) + "'"
    def text2text(self, line):
        m = re.match(self.subVar, line)
        if (self.enableSealedSubstitution and m):
            if len(m.group(2))==0:
                return m.group(1) + self.subZeroReplace + self.text2text(m.group(3))
            else:
                return m.group(1) + str(eval(m.group(2), self.globalvars)) + self.text2text(m.group(3))
        else:
            return line        
    def indentCodeLine(self, indent, s):
        if (len(indent) != 0):
            return s + 'fast.lastIndent = \"' + indent + '\"' + self.newline + s + 'fast.indent+=\"' + indent + '\"' + self.newline
        else:
            return ''
    def dedentCodeLine(self, indent, s):
        if (len(indent) != 0):
            return s + 'fast.indent=fast.indent[0:len(fast.indent)-' + str(len(indent)) + ']' + self.newline
        else:
            return ''
    def _findFile(self, fn):
        # Search for non-hardpath fn in current dir, ./pkg, user dir, finally $FAST_INSTALL_PATH/pkg
        if ((fn[0] == '/') or (os.path.isfile(fn))):
            return fn
        if (os.path.isfile('pkg/' + fn)):
            return 'pkg/' + fn
        # user dir for FAST packages must be specified by env var, FAST_INC_PATH
        if ('FAST_INC_PATH' in os.environ):
            pfn = os.environ['FAST_INC_PATH'] + '/' + fn
            if (os.path.isfile(pfn)):
                return pfn
        # look in install dir
        pfn = self.installPath + '/pkg/' + fn
        if (os.path.isfile(pfn)):
            return pfn
        # Unable to find it
        return fn

    def _process(self, fn):
        line = self.line
        lineNum = self.lineNum
        m0 = re.match(self.immCodePrefix, line)
        m1 = re.match(self.codePrefix, line)
        ci = ' '*self.codeIndent  # code indention (string of spaces)
        if (m0): # this is Python code to be executed now
            #print('Executing: ' + m0.group(1))
            exec(m0.group(1) + self.newline, self.globalvars)
        elif (m1): # this is Python code for 2nd pass
            #indent = len(m1.group(1)) # output indent
            indent = m1.group(1) # output indent string
            if (re.match(r'^#', m1.group(3))):
                m2 = False
                m3 = False
                m4 = False
            else:
                m2 = re.match(r'^(.*:)\{\s*$', m1.group(3)) or re.match(r'^(.*:)\{\s*#', m1.group(3)) # begin code block
                m3 = re.match(r'\{\s*$', m1.group(3)) or re.match(r'\{\s*#', m1.group(3)) # begin code block
                m4 = re.match(r'\}\s*$', m1.group(3)) or re.match(r'\}\s*#', m1.group(3)) # end code block
            if (self.codeIndent == 0): # ignore spaces in line if within code brackets { .. }
                ci = m1.group(2)       # code indention (string of spaces specified in the line)
            if (m2):
                self.srcCode += ci +  m2.group(1) + self.newline
                self.codeIndent += 1
            elif (m3):
                self.codeIndent += 1
            elif (m4):
                self.codeIndent -= 1
                if (self.codeIndent < 0):
                    print('fast: ERROR at line ' + str(lineNum) + ' in file ' + fn + ' - "' + line + '"\n')
                    print('fast: ERROR at line ' + str(lineNum) + ' in file ' + fn + ' - "}" (code block end) has no matching "{" (code block begin)')
                    self.codeIndent = 0
            else:
                self.srcCode += self.indentCodeLine(indent, ci)  # support output-indented function calls
                self.srcCode += ci +  m1.group(3) + self.newline
                self.srcCode += self.dedentCodeLine(indent, ci)
        else: # plain text possibly with Python expression substitutions
            self.srcCode += ci + 'fast.printWithIndent(' + self.text2code(line.rstrip(self.newline)) + ')' + self.newline

    def _processSection(self, line):
        #print('_processSection called with line below')
        #print(line)
        #print('----')
        m1 = re.match(self.codePrefix, line)
        if (m1): # in this case, execute this code now
            indent = m1.group(1) # output indent string
            self.indent+=indent
            #print('_processSection: evaluating.. ' + m1.group(3))
            exec(m1.group(3) + self.newline, self.globalvars)
            self.indent=self.indent[0:len(self.indent)-len(indent)]
        else: # plain text possibly with Python expression substitutions
            #print('_processSection: printing.. ' + line)
            self.printWithIndent(self.text2text(line));

    def _includeSectionProcess(self, section):
        #print('includeSection: called with section "' + section + '" ..')
        #for s in self.sections:
        #    print('includeSection: "' + s + '"')
        if (self.includeSectionDepth >= self.recursionLimit):
            print('fast: FATAL ERROR - includeSection calls exceeded limit of ' + str(self.recursionLimit))
            raise RuntimeError('fast: FATAL ERROR - includeSection calls exceeded limit of ' + str(self.recursionLimit))
        else:
            self.includeSectionDepth += 1
        tmp = self.tmpSection + str(self.includeSectionDepth)
        +self < tmp
        self.sections[tmp].isTemporary = True
        if (section in self.sections):
            #print('includeSection: processing section "' + section + '" ..')
            for line in self.getLines(section): ##self.sections[section].text.rstrip(self.newline).splitlines():
                self._processSection(line)
            # Remove temporary section
            if self.sections[section].isTemporary:
                #print('Deleting temporary section ' + section)
                del self.sections[section]
        -self
        self.includeSectionDepth -= 1
        return tmp

    def includeSection(self, section):
        tmp = self._includeSectionProcess(section)
        if (tmp in self.sections):
            self.printSection(tmp)
            #del self.sections[tmp] ## remove my temporary section
        return self

    def includeSectionChomp(self, section, c=',', linecc='//'):
        tmp = self._includeSectionProcess(section)
        if (tmp in self.sections):
            self.chomp(c, linecc).printSection(tmp)
            #del self.sections[tmp]
        return self

    def addImportPath(self, path):
        if (os.path.exists(path)):
            sys.path.insert(0, path)
        return self

    def include(self, fn, skipFirstLines=0):
        #print('Opening file: ' + fn + ' skipFirstLines=' + str(skipFirstLines))
        fn = self._findFile(fn)
        self.lineNum = 0
        with open(fn) as file:
            for self.line in file:
                self.lineNum += 1
                if (self.lineNum == 1):
                    self.firstLine = self.line
                if (self.lineNum > skipFirstLines):
                    self._process(fn)
        return self

    def printCode(self):
        print('''\
from __future__ import print_function
import sys
import os
def _insertIfExists(x):
    if (os.path.exists(x)):
        sys.path.insert(0,x)
if ('FAST_INSTALL_PATH' in os.environ):
    installPath = os.environ['FAST_INSTALL_PATH']
else:
    installPath = '~/python/pet'
_insertIfExists(installPath + '/pkg')
if ('FAST_INC_PATH' in os.environ):
    _insertIfExists(os.environ['FAST_INC_PATH'])
_insertIfExists(os.getcwd() + '/pkg')
sys.path.insert(0, os.getcwd())
import fast_classes
re = fast_classes.re
time = fast_classes.time
textwrap = fast_classes.textwrap
fast = fast_classes.FastClass(dict())
(info,doc,args) = fast_classes.setup(fast, installPath, True)

#------------------ FAST GLOBALS GO HERE -------------------------
# Note: Your global vars, if you define any, must be added to this script manually.





#------------------ FAST STARTS HERE AT LINE 31 ------------------''')
        print(self.srcCode)
        print('''\
fast_classes.info(fast, args)
''')
    def printme(self):
        exec(self.srcCode, self.globalvars)
    def createSection(self, _section=''):
        return SectionBase(self, _section)
    def printWithIndent(self,s):
        if (len(self.section) == 0):
            if (self.enable and (not self.infoFlag)):
                print(self.indent + s)
        else:
            if (self.section not in self.sections):
                self.sections[self.section] = self.createSection(self.section)
            #print('Dumping "' + s + '" to section "' + self.section + '"')
            self.sections[self.section] += self.indent + s + self.newline
        return self
    def getInfoSectionHeader(self,section):
        #line1 = self.sections[section].getText().split(self.newline)[0]
        line1 = self.sections[section].getText().splitlines()[0]
        m = re.match(re.compile('^\s*.*?(\(.*?\))\s+(.*)'), line1)
        if (m):
            flen = len(section) - 5 + len(m.group(1))
            self.infoDict[section[5:] + m.group(1)] = m.group(2)
        else:
            flen = len(section) - 5
            self.infoDict[section[5:]] = line1
        if (flen > self.maxFctNameLength):
            self.maxFctNameLength = flen

    def getSection(self,section):
        if (section in self.sections):
            return self.sections[section].getText()
        else:
            return ''
    def getLines(self,section):
        return self.getSection(section).splitlines()
    def setSection(self,section,text):
        self.sections[section].setText(text)
    def printSection(self,section):
        if (type(section) != str):
            section = section.section ## get property of object
        if (len(self.indent) > 0):
            self.dedentSection(section)
        if (len(self.section) == 0): ## print to STDOUT
            if (self.enable and (not self.infoFlag) and (section in self.sections)):
                for s in self.getLines(section):
                    print(self.indent + s)
        else:
            if (self.section == section):
                print('fast: ERROR - printSection is not allowed to print a section to itself (' + section + ')')
            elif (section in self.sections):
                if (self.section not in self.sections):
                    self.sections[self.section] = self.createSection(self.section)
                for s in self.getLines(section):
                    self.sections[self.section] += self.indent + s + self.newline
        # Remove temporary section
        if self.sections[section].isTemporary:
            #print('Deleting temporary section ' + section)
            del self.sections[section]
        return self
    def dedentSection(self,section):
        if (section in self.sections):
            self.sections[section].setText(textwrap.dedent(self.sections[section].getText()))
        return self
    def copyUnsealedFileSection(self, sfn):
        # Write unsealed fn section to the temporary section
        tmp = self.tmpSection
        +self < tmp
        self > sfn   # calls includeSection to process placeholders
        -self
        del self.sections[sfn]  # remove fn section
        #self <= tmp  # dedent temp section
        return tmp
    def writeFile(self, sfn, fn, chompMe=False, c=',', linecc='//'):
        if ((not self.infoFlag) and (sfn in self.sections)):
            if (self.sealIncludeSection):
                self.unseal()  ## unseal all included subsections
                tmp = self.copyUnsealedFileSection(sfn)
                self.sealIncludeSection = True
            else:
                tmp = sfn  ## do not unseal
            if (chompMe):
                self.removeLastChar(tmp, c, linecc)  ## chomp the temp section
            with open(fn, 'w') as file:
                for s in self.sections[tmp].getText().rstrip(self.newline).splitlines():
                    file.write(s + self.newline)
            del self.sections[tmp]
        return self
    def writeFiles(self):
        z = self.sections.copy()  ## copy
        for x in z:
            #print('Writing section ' + x)
            z[x].write()
    def __pos__(self):  ## (push)
        self.stack += [self.section, self.enable, self.indent]
        self.enable = False
        self.section = ''
        self.indent = ''
        return self
    def setFileName(self, fn=''):
        secObj = self[self.section]
        if (secObj):
            fn = fn if fn else self.section
            secObj(fn)
            return True
        else:
            return False
    def getFileName(self):
        secObj = self[self.section]
        fn = secObj.fn if secObj else ''
        return fn
    def __neg__(self):  ## (pop)
        #fn = self.getFileName()
        #if (fn):
            #self.writeFile(self.section, fn)
        #    self[self.section].write(fn)
        self.indent = self.stack.pop()
        self.enable = self.stack.pop()
        self.section = self.stack.pop()
        return self
    def __getitem__(self, _section):
        if (_section in self.sections):
            return self.sections[_section]
        else:
            return None
    def __call__(self, cs='', tsflag=True):
        if (not self.infoFlag):
            cs = cs or self.commentString
            dt = time.strftime('%m/%d/%Y') if tsflag else '##/##/####'
            tm = time.strftime('%H:%M:%S') if tsflag else '##:##:##'

            self.printWithIndent('')
            self.printWithIndent(cs + '**********************************************************************')
            self.printWithIndent(cs + '**********************************************************************')
            self.printWithIndent(cs)
            self.printWithIndent(cs + '   D O   N O T   H A N D - E D I T   T H I S   F I L E   !!!!!')
            self.printWithIndent(cs)
            self.printWithIndent(cs + ' This file was generated by ' + self.srcFile + ' on ' + dt)
            self.printWithIndent(cs + ' at time ' + tm + ' with FAST Version ' + self.version)
            self.printWithIndent(cs + ' Do not edit this file directly. Edit its source, ' + self.srcFile)
            self.printWithIndent(cs + ' Otherwise, your work is likely to be overwritten.')
            self.printWithIndent(cs)
            self.printWithIndent(cs + ' Documentation for FAST is found here:')
            self.printWithIndent(cs + ' ' + self.docUrl)
            self.printWithIndent(cs)
            self.printWithIndent(cs + '**********************************************************************')
            self.printWithIndent(cs + '**********************************************************************')
        return self
    def __rshift__(self, x):
        self.indent += ' ' * x
    def __gt__(self, x):
        if (self.sealIncludeSection and len(self.section)):
            #print('Printing placeholder for section ' + x)
            self.printWithIndent(self.commentString + self.codeChar + "fast.includeSection('" + x + "')")
        else:
            self.includeSection(x)
        return self
    def seal(self):
        self.sealIncludeSection = True
        return self
    def unseal(self):
        self.sealIncludeSection = False
        return self
    def __lshift__(self, x):
        if (len(self.indent) >= x):
            self.indent = self.indent[0:len(self.indent)-x]
        else:
            self.indent = ''
        return self
    def __lt__(self, x):
        if ((x in self.sectionDisable) and self.sectionDisable[x]):
            if (len(self.stack) == 0):
                self.section = ''
                self.enable = True
            else:
                -self
                self.stack += [self.section, self.enable, self.indent]
        else:
            self.section = x
            if (self.section not in self.sections):
                self.sections[self.section] = self.createSection(self.section)
    def __le__(self, x):
        self.dedentSection(x)
    def __ge__(self, x):
        self.printWithIndent(x)
    def off(self):
        self.enable = False
        return self
    def on(self):
        self.enable = True
        return self
    def readFile(self, fn, commentStr='//'):
        rv = []
        with open(fn) as file:
            for line in file:
                if not (re.match(r'^\s*$', line) or re.match(re.compile('^\s*' + commentStr), line)):
                    rv += [line]
        return rv
    def removeLastChar(self, x, c=',', commentStr='//'):
        if (x == ''):
            print('fast.removeLastChar(): ERROR - No section specified')
        if (x in self.sections):
            buf = self.sections[x].getText().rstrip(self.newline).splitlines()
            if (len(buf)):
                if (len(commentStr)):
                    m = re.match(re.compile('^(.*?)(' + c + '?)(\s*)' + commentStr + '(.*)$'), buf[-1])
                    if (m):
                        s = m.group(3)  # keep spacing to line comment the same
                        if (m.group(2) == c):
                            s += ' '
                            buf[-1] = m.group(1) + s + commentStr + m.group(4)
                    else:
                        buf[-1] = buf[-1].rstrip().rstrip(c)
                else:
                    buf[-1] = buf[-1].rstrip().rstrip(c)
                    self.sections[x].setText(self.newline.join(buf) + self.newline)
        else:
            print('fast.removeLastChar(): ERROR - ' + x + ' is not a defined section')
        return self
    def soff(self, x):
        self.sectionDisable[x] = True
        return self
    def son(self, x):
        self.sectionDisable[x] = False
        return self

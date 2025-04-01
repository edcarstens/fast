import re
class SectionBase(object):
    # Class variables
    _uniqueSectionNum = 0
    @classmethod
    def _uniqueSectionName(self):
        rv = '___section' + str(self._uniqueSectionNum) + '___'
        SectionBase._uniqueSectionNum += 1
        return rv
    
    def __init__(self, _fast, section='', parent=None):
        self.fast = _fast
        self.section = section or self._uniqueSectionName()
        self.subsection = ''
        self.parent = parent
        self.warnOn = True
        self.infoOn = True
        self.processEnable = True
        self.text = '' # New - every section object stores its own text
        self.fn = ''   # set to filename for file section
        self.chomp = SectionChompClass(self.fast, self)
        self.rstrip = self.chomp
        self.fast.sections[self.section] = self  # register me with fast.sections
        self.isTemporary = False  # temporary flag for deletion after printing section
    def __call__(self, fn=''):
        self.fn = fn if fn else self.section.split()[-1]
        return self
    def __iadd__(self, s):
        self.setText(self.getText() + s)
        return self
    def __pos__(self):
        self.subsection = ''
        +self.fast < self.section
        return self
    def makeValidName(self, _x):
        x = re.sub('\W','_',_x)
        if (not re.match('[_a-zA-Z]', x[0])):
            x = '_' + x
        if (x != _x) and self.warnOn:
            print('SectionBase.makeValidName: Warning - python attribute name "' + x + '" does not match section name "' + _x + '"')
        return x
    def create(self, _section='', parent=None):
        return SectionBase(self.fast, _section, parent)
    def __getattr__(self, subsection):
        #print('getattr called with ' + subsection)
        self.subsection = subsection
        #x = self.makeValidName(subsection)
        sec = self.create(self.section + ' ' + self.subsection, self)
        #setattr(self, x, sec)
        setattr(self, self.subsection, sec)
        return sec
    def __neg__(self):
        -self.fast
        self.process()
        return self
    def _gt_helper(self, subsection):
        """ helper function for implementing __gt__ and chomp.__gt__ """
        if (len(subsection)):
            x = self.makeValidName(subsection)
            sub = getattr(self, x)
            #print('_gt_helper created ' + sub.section + ' and ' + x)
            mysec = sub
        else:
            mysec = self
        
        if (self.processEnable):
            self.processEnable = False  # process only once
            if (self.fast.sealIncludeSection and len(self.fast.section)):
                self.fast.printWithIndent(self.fast.commentString + self.fast.codeChar + "fast.sections['" + mysec.section + "'].processFinal()")
            else:
                mysec.processFinal()
        self.fast > mysec.section
    def __gt__(self, subsection):
        self._gt_helper(subsection)
    def write(self, fn=''):
        if (len(fn) == 0):
            if (self.fn):
                fn = self.fn
            #else:
            #    fn = self.makeValidName(self.section)
        if (fn):  ## don't do anything for non-file sections
            if (self.infoOn):
                +self.fast
                self.fast.on() >= 'SectionBase.write: Info - writing section (' + self.section + ') to file "' + fn + '"'
                -self.fast
            self.fast.writeFile(self.section, fn)
        return self
    def process(self):
        """
        Implement this method in your subclass if you need to
        process input chunks sooner than processFinal. This
        method is always called from the __neg__ method.
        You may use getLines() to loop through the section line by
        line:
        
        //. for line in self.getLines():{

        The processed contents can be passed to setText, or one
        can clear the section and rewrite it, and/or one can write
        output to other sections or subsections.
        """
        pass
    def processFinal(self):
        """
        Implement this method in your subclass if you need to
        process input section(s) prior to writing output section(s).
        You may use getLines() to loop through the section line by
        line:
        
        //. for line in self.getLines():{

        The processed contents can be passed to setText, or one
        can clear the section and rewrite it, and/or one can write
        output to other sections or subsections.
        """
        pass
    def getText(self):
        return self.text
    def getLines(self):
        return self.text.splitlines()
    def setText(self, text):
        self.text = text

class SectionChompClass(object):
    """ chomp class """
    def __init__(self, _fast, parent):
        self.fast = _fast
        self.parent = parent
        self.c = ','
        self.linecc = '//'
    def __call__(self, c=',', lcc='//'):
        self.c = c
        self.linecc = lcc
        return self
    def __gt__(self, x):
        self.fast.chomp(self.c, self.linecc)
        self.parent._gt_helper(x)

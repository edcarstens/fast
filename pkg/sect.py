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
        self.chomp = SectionChompClass(_fast,parent)
        self.fast.sections[self.section] = self  # register me with fast.sections
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
    def __lt__(self, subsection):
        print('SectionBase.__lt__: Warning - Deprecated as of FAST version 4.0')
        self.subsection = subsection
        if (len(subsection)):
            self.fast < (self.section + ' ' + self.subsection)
        else:
            self.fast < self.section
        return self
    def __getattr__(self, subsection):
        #print 'getattr called'
        self.subsection = subsection
        x = self.makeValidName(subsection)
        sec = self.create(self.section + ' ' + self.subsection, self)
        setattr(self, x, sec)
        return sec
    def __le__(self, subsection):
        print('SectionBase.__le__: Warning - Deprecated as of FAST version 4.0')
        self.subsection = subsection
        if (len(subsection)):
            self.fast < (self.section + ' ' + self.subsection)
            x = self.makeValidName(subsection)
            if (x not in self.__dict__):
                setattr(self, x, self.create(self.fast.section, self))
        else:
            self.fast < self.section
        return self
    def __neg__(self):
        -self.fast
        self.process0()
        return self
    def __gt__(self, subsection):
        if (self.processEnable):
            self.processEnable = False  # process only once
            self.process()
        if (len(subsection)):
            self.fast > (self.section + ' ' + subsection)
        else:
            self.fast > self.section
    def write(self, fn=''):
        if (len(fn) == 0):
            fn = self.makeValidName(self.section) # + '.txt' # default filename
        if (self.infoOn):
            +self.fast
            self.fast.on() >= 'SectionBase.write: Info - writing section to file ' + fn
            -self.fast
        #+self.fast < ('file:' + fn)
        #self > ''
        #-self.fast
        self.fast.writeFile(fn, fn)

    def process0(self):
        """
        Implement this method in your subclass if you need to
        process input section(s) immediately upon read-in. This
        method is always called from the __neg__ method.
        You may use getLines() to loop through the section line by
        line:
        
        //. for line in self.getLines():

        The processed contents can be passed to setText, or one
        can clear the section and rewrite it, and/or one can write
        output to other sections or subsections.
        """
        pass
    def process(self):
        """
        Implement this method in your subclass if you need to
        process input section(s) prior to writing output section(s).
        You may use getLines() to loop through the section line by
        line:
        
        //. for line in self.getLines():

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
    def __init__(self, _fast, parent=None):
        self.fast = _fast
        self.parent = parent
        self.c = ','
        self.linecc = '//'
    def __call__(self, c=',', lcc='//'):
        self.c = c
        self.linecc = lcc
        return self
    def __gt__(self, x):
        if x:
            section = self.parent.section + ' ' + x
        else:
            section = self.parent.section
        self.fast.chomp(self.c, self.linecc) > section

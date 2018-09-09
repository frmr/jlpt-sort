import codecs
from sets import Set

class Kanji:
        def __init__(self, parts, level):
                self.char = parts[0][0]
                self.onyomi = parts[1]
                self.kunyomi = parts[2]
                self.meaning = parts[3]
                self.level = level
                self.score = 0
                
class Vocab:
        def __init__(self, line, level):
                parts = SplitCsvLine(line)
                self.textKanji = parts[0]
                self.textKana = parts[1]
                self.meaning = parts[2]
                self.level = level
                self.hasUnknownChars = False

        def ContainsUnknownChar(self, kanaList, miscList, kanjiDict):
                for char in self.textKanji:
                        if char not in kanaList and char not in miscList and char not in kanjiDict:
                                self.hasUnknownChars = True
                                return True 

                return False

        def GivePointsToKanji(self, kanjiDict):
                for char in self.textKanji:
                        if char in kanjiDict:
                                kanjiDict[char].score += 1

def LoadFile(filename):
        lines = []
        for line in codecs.open(filename, "r", "utf-8"):
                lines.append(line)

        return lines
                
def SplitCsvLine(line):
        parts = [""]
        quoted = False
        for char in line:
                if char == '"':
                        quoted = not quoted
                elif char == ',' and quoted == False:
                        parts.append("")
                else:
                        parts[-1] += char
                
        return parts

def LoadKanaFile(filename):
        lines = LoadFile(filename)
        kanaList = []
        for line in lines:
                kanaList.append(line[0])

        return kanaList
        
def LoadKanjiFile(filename, level):
        lines = LoadFile(filename)
        kanjiDict = {}
        for line in lines:
                parts = SplitCsvLine(line)
                kanjiDict[parts[0]] = Kanji(parts, level)

        return kanjiDict

def LoadMiscFile(filename):
        lines = LoadFile(filename)
        miscList = []
        for line in lines:
                miscList.append(line[0])

        return miscList
        
def LoadVocabFile(filename, level):
        lines = LoadFile(filename)
        vocabList = []
        for line in lines:
                vocabList.append(Vocab(line, level))

        return vocabList

def LoadKana():
        kanaList = LoadKanaFile("kana/hiragana.csv")
        kanaList += LoadKanaFile("kana/katakana.csv")        
        return kanaList
        
def LoadKanji():
        kanjiDict = LoadKanjiFile("kanji/n5.csv", 5)
        kanjiDict.update(LoadKanjiFile("kanji/n4.csv", 4))
        kanjiDict.update(LoadKanjiFile("kanji/n3.csv", 3))
        kanjiDict.update(LoadKanjiFile("kanji/n2.csv", 2))
        return kanjiDict

def LoadMisc():
        miscList = LoadMiscFile("misc/misc.csv")
        return miscList
        
def LoadVocab():
        vocabList = LoadVocabFile("vocab/n5.csv", 5)
        vocabList += LoadVocabFile("vocab/n4.csv", 4)
        vocabList += LoadVocabFile("vocab/n3.csv", 3)
        vocabList += LoadVocabFile("vocab/n2.csv", 2)
        return vocabList

def GetSortedKanji(kanjiDict):
        kanjiSet = Set()

        for key, value in kanjiDict.iteritems():
                kanjiSet.add(value.score)

        sortedKanji = []
        for score in kanjiSet:
                foundItems = []
                for key, value in kanjiDict.iteritems():
                        if value.score == score:
                                foundItems.append(key)

                sortedKanji += foundItems
                
        return reversed(sortedKanji)

def TagVocab(inString, kanjiDict, kanaList, miscList):
        outString = ""

        for char in inString:
                
                linkedChar = char

                hashSign = '#'

                if char in kanjiDict:
                        linkedChar = "<a href='" + hashSign + char + "'>" + char + "</a>"
                
                if char in kanjiDict or char in kanaList or char in miscList:
                        outString += linkedChar
                else:
                        outString += "<span class='unknown-char'>" + linkedChar + "</span>"

        return outString

def WriteVocabToHtmlFile(htmlFile, vocab, kanjiDict, kanaList, miscList):
        htmlFile.write("<div class='vocab-entry'>")
        
        htmlFile.write("<div class='vocab-entry_kanji'>")
        htmlFile.write(TagVocab(vocab.textKanji, kanjiDict, kanaList, miscList))
        htmlFile.write("</div>")

        htmlFile.write("<div class='vocab-entry_kana'>")
        htmlFile.write(vocab.textKana)
        htmlFile.write("</div>")

        htmlFile.write("<div class='vocab-entry_meaning'>")
        htmlFile.write(vocab.meaning)
        htmlFile.write("</div>")

        htmlFile.write("</div>")

def WriteVocabListToHtmlFile(htmlFile, vocabList, kanjiDict, kanaList, miscList):
        for level in range(5, 1, -1):
                for vocab in vocabList:
                        if vocab.level == level:
                                WriteVocabToHtmlFile(htmlFile, vocab, kanjiDict, kanaList, miscList)

def WriteHtml(kanjiDict, kanaList, miscList, vocabList, filename):        
        htmlFile = codecs.open(filename, "w", "utf-8")

        htmlFile.write("<html>")

        htmlFile.write("<head><link rel='stylesheet' href='jlpt-sort.css'></head>")

        htmlFile.write("<body>")
        
        for kanji in GetSortedKanji(kanjiDict):

                thisKanjiVocab = []
                for vocab in vocabList:
                        if kanji in vocab.textKanji:
                                thisKanjiVocab.append(vocab)

                htmlFile.write("<div class='section'>")
                
                htmlFile.write("<div class='title'>" + "<a href='http://jisho.org/search/" + kanji + "%23kanji" + "' name='" + kanji + "'>" + kanji + "</a>" + "</div>")
                
                htmlFile.write("<div class='vocab-block'>")

                WriteVocabListToHtmlFile(htmlFile, thisKanjiVocab, kanjiDict, kanaList, miscList)

                htmlFile.write("</div>")

                htmlFile.write("</div>")
                htmlFile.write("</div>")
                
        htmlFile.write("</body>")
        htmlFile.write("</html>")

        htmlFile.close()
        
def Main():
        kanaList = LoadKana();
        miscList = LoadMisc();
        kanjiDict = LoadKanji();
        vocabList = LoadVocab();

        for vocab in vocabList:
                if not vocab.ContainsUnknownChar(kanaList, miscList, kanjiDict):
                        vocab.GivePointsToKanji(kanjiDict)

        WriteHtml(kanjiDict, kanaList, miscList, vocabList, "jlpt-sort.html")

        print "Done"

Main()

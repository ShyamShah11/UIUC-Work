import metapy

def tokens_lowercase(doc):
    #Write a token stream that tokenizes with ICUTokenizer, 
    #lowercases, removes words with less than 2 and more than 5  characters
    #performs stemming and creates trigrams (name the final call to ana.analyze as "trigrams")
    tok = metapy.analyzers.ICUTokenizer(suppress_tags=True) #ICUTokenizer without end/start tags
    tok = metapy.analyzers.LowercaseFilter(tok) #lowercases
    tok = metapy.analyzers.LengthFilter(tok, min=2, max=5) #remove words with less than 2 and more than 5 chars
    tok = metapy.analyzers.Porter2Filter(tok) #stemming
    ana = metapy.analyzers.NGramWordAnalyzer(3, tok) #creates trigrams
    trigrams = ana.analyze(doc)
    tok.set_content(doc.content())
    tokens = [token for token in tok]
    #leave the rest of the code as is
    tok.set_content(doc.content())
    tokens, counts = [], []
    for token, count in trigrams.items():
        counts.append(count)
        tokens.append(token)
    return tokens
    
if __name__ == '__main__':
    doc = metapy.index.Document()
    doc.content("I said that I can't believe that it only costs $19.95! I could only find it for more than $30 before.")
    print(doc.content()) #you can access the document string with .content()
    tokens = tokens_lowercase(doc)
    print(tokens)

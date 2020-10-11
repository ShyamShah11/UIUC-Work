import numpy as np
import math


def normalize(input_matrix):
    """
    Normalizes the rows of a 2d input_matrix so they sum to 1
    """

    row_sums = input_matrix.sum(axis=1)
    try:
        assert (np.count_nonzero(row_sums)==np.shape(row_sums)[0]) # no row should sum to zero
    except Exception:
        raise Exception("Error while normalizing. Row(s) sum to zero")
    new_matrix = input_matrix / row_sums[:, np.newaxis]
    return new_matrix

       
class Corpus(object):

    """
    A collection of documents.
    """

    def __init__(self, documents_path):
        """
        Initialize empty document list.
        """
        self.documents = []
        self.vocabulary = []
        self.likelihoods = []
        self.documents_path = documents_path
        self.term_doc_matrix = None 
        self.document_topic_prob = None  # P(z | d)
        self.topic_word_prob = None  # P(w | z)
        self.topic_prob = None  # P(z | d, w)

        self.number_of_documents = 0
        self.vocabulary_size = 0

    def build_corpus(self):
        """
        Read document, fill in self.documents, a list of list of word
        self.documents = [["the", "day", "is", "nice", "the", ...], [], []...]
        
        Update self.number_of_documents
        """
        #create a list of lists 
        f = open(self.documents_path,"r")
        self.documents=[[word.strip() for word in line.split(" ")] for line in f.read().split("\n")]
        f.close()
        #remove the 0 or 1 in the test dataset
        for i in range (len(self.documents)):
            temp=self.documents[i][0].split("\t")
            if (len(temp)>1):
                self.documents[i][0] = temp[-1]
            #remove any blank entries
            try:
                self.documents[i].remove('')
            except:
                pass

        #set number of documents
        self.number_of_documents=len(self.documents)

    def build_vocabulary(self):
        """
        Construct a list of unique words in the whole corpus. Put it in self.vocabulary
        for example: ["rain", "the", ...]

        Update self.vocabulary_size
        """
        #flatten self.documents and remove duplicates
        self.vocabulary = list(dict.fromkeys([word for line in self.documents for word in line]))
        #set vocabulary size
        self.vocabulary_size=len(self.vocabulary)

    def build_term_doc_matrix(self):
        """
        Construct the term-document matrix where each row represents a document, 
        and each column represents a vocabulary term.

        self.term_doc_matrix[i][j] is the count of term j in document i
        """
        #count number of voc word occurrences in each document as a numpy array
        self.term_doc_matrix=np.asarray([[doc.count(term) for term in self.vocabulary] for doc in self.documents])
        


    def initialize_randomly(self, number_of_topics):
        """
        Randomly initialize the matrices: document_topic_prob and topic_word_prob
        which hold the probability distributions for P(z | d) and P(w | z): self.document_topic_prob, and self.topic_word_prob

        Don't forget to normalize! 
        HINT: you will find numpy's random matrix useful [https://docs.scipy.org/doc/numpy-1.15.0/reference/generated/numpy.random.random.html]
        """
        #initialize them first
        self.document_topic_prob=np.random.rand(self.number_of_documents,2)
        self.topic_word_prob=np.random.rand(2,self.vocabulary_size)
        #normalize them 
        for rownum in range(len(self.document_topic_prob)):
            self.document_topic_prob[rownum]/=np.sum(self.document_topic_prob[rownum])
        for rownum in range(len(self.topic_word_prob)):
            self.topic_word_prob[rownum]/=np.sum(self.topic_word_prob[rownum])

    def initialize_uniformly(self, number_of_topics):
        """
        Initializes the matrices: self.document_topic_prob and self.topic_word_prob with a uniform 
        probability distribution. This is used for testing purposes.

        DO NOT CHANGE THIS FUNCTION
        """
        self.document_topic_prob = np.ones((self.number_of_documents, number_of_topics))
        self.document_topic_prob = normalize(self.document_topic_prob)

        self.topic_word_prob = np.ones((number_of_topics, len(self.vocabulary)))
        self.topic_word_prob = normalize(self.topic_word_prob)

    def initialize(self, number_of_topics, random=False):
        """ Call the functions to initialize the matrices document_topic_prob and topic_word_prob
        """
        print("Initializing...")

        if random:
            self.initialize_randomly(number_of_topics)
        else:
            self.initialize_uniformly(number_of_topics)

    def expectation_step(self):
        """ The E-step updates P(z | w, d)
        """
        print("E step:")
        #iterate over documents
        for i in range (self.number_of_documents):   
            #calculate each topic individually 
            first_topic=self.document_topic_prob[i][0]*self.topic_word_prob[0]        
            second_topic=self.document_topic_prob[i][1]*self.topic_word_prob[1]
            #get the sum of their values
            norm=first_topic+second_topic
            #return the normalized value
            self.topic_prob[i]=np.asarray([np.divide(first_topic,norm),np.divide(second_topic,norm)])
            

    def maximization_step(self, number_of_topics):
        """ The M-step updates P(w | z)
        """
        print("M step:")

        # update P(z | d)
        #iterate over docs
        for i in range(self.number_of_documents):
            #iterate over topics
            for j in range(number_of_topics):
                numerator=0
                for k in range(self.vocabulary_size):
                    numerator+=self.term_doc_matrix[i][k]*self.topic_prob[i][j][k]
                self.document_topic_prob[i][j]=numerator
            #normalizing
            self.document_topic_prob[i]/=np.sum(self.document_topic_prob[i])



"""
I attempted to do this with matrix multiplication but couldn't figure all of it out so switched over to for loops

#calculate the updated values
self.document_topic_prob[i]=self.term_doc_matrix[i]*np.transpose(self.topic_prob[i])
#normalize them
self.document_topic_prob[i]=self.document_topic_prob[i]/np.sum(self.document_topic_prob[i])
"""
        
        
        # update P(w | z)
        #iterate over topics
        for i in range(number_of_topics):
            #iterate over words
            for j in range (self.vocabulary_size):
                numerator=0
                #iteratve over docs
                for k in range(self.number_of_documents):
                    numerator+=self.term_doc_matrix[k][j]*self.topic_prob[k][i][j]
                self.topic_word_prob[i][j] = numerator
            #normalizing
            self.topic_word_prob[i]/=np.sum(self.topic_word_prob[i])


    def calculate_likelihood(self, number_of_topics):
        """ Calculate the current log-likelihood of the model using
        the model's updated probability matrices
        
        Append the calculated log-likelihood to self.likelihoods

        """
        likelihood=0
        #iterate over docs
        for i in range (self.number_of_documents):
            #iterate over words
            for j in range(self.vocabulary_size):
                sum=0
                #iterate over topics
                for k in range(number_of_topics):
                    sum+=self.document_topic_prob[i][k]*self.topic_word_prob[k][j]
                likelihood+=self.term_doc_matrix[i][j]*np.log(sum)
        #print (likelihood)
        self.likelihoods.append(likelihood)
        return

    def plsa(self, number_of_topics, max_iter, epsilon):

        """
        Model topics.
        """
        print ("EM iteration begins...")
        
        # build term-doc matrix
        self.build_term_doc_matrix()
        
        # Create the counter arrays.
        
        # P(z | d, w)
        self.topic_prob = np.zeros([self.number_of_documents, number_of_topics, self.vocabulary_size], dtype=np.float)

        # P(z | d) P(w | z)
        self.initialize(number_of_topics, random=True)

        # Run the EM algorithm
        current_likelihood = 0.0

        for iteration in range(max_iter):
            print("Iteration #" + str(iteration + 1) + "...")


            self.expectation_step()
            self.maximization_step(number_of_topics)
            self.calculate_likelihood(number_of_topics)
            try:
                if (abs(self.likelihoods[-1]-self.likelihoods[-2])<=epsilon):
                    return
            except:
                pass


def main():
    documents_path = 'data/test.txt'
    corpus = Corpus(documents_path)  # instantiate corpus
    corpus.build_corpus()
    corpus.build_vocabulary()
    print(corpus.vocabulary)
    print("Vocabulary size:" + str(len(corpus.vocabulary)))
    print("Number of documents:" + str(len(corpus.documents)))
    number_of_topics = 2
    max_iterations = 50
    epsilon = 0.001
    corpus.plsa(number_of_topics, max_iterations, epsilon)



if __name__ == '__main__':
    main()

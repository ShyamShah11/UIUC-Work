import math
import sys
import time
from scipy import stats #need to remove all scipy dependencies before submitting
import metapy
import pytoml

class InL2Ranker(metapy.index.RankingFunction):
    """
    Create a new ranking function in Python that can be used in MeTA.
    """
    def __init__(self, some_param=1.0):
        self.param = some_param
        # You *must* call the base class constructor here!
        super(InL2Ranker, self).__init__()

    def score_one(self, sd):
        """
        You need to override this function to return a score for a single term.
        For fields available in the score_data sd object,
        @see https://meta-toolkit.org/doxygen/structmeta_1_1index_1_1score__data.html
        """
        def tfn(sd):
            return sd.doc_term_count * math.log((1+(sd.avg_dl/sd.doc_size)),2)

        return (sd.query_term_weight) * (tfn(sd)/(tfn(sd)+self.param)) * (math.log((sd.num_docs+1)/(sd.corpus_term_count+0.5),2))


def load_ranker(cfg_file):
    """
    Use this function to return the Ranker object to evaluate, e.g. return InL2Ranker(some_param=1.0) 
    The parameter to this function, cfg_file, is the path to a
    configuration file used to load the index. You can ignore this for MP2.
    """
    return InL2Ranker(some_param=1.0)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: {} config.toml".format(sys.argv[0]))
        sys.exit(1)

    cfg = sys.argv[1]
    print('Building or loading index...')
    idx = metapy.index.make_inverted_index(cfg)
    ranker_in = load_ranker(cfg)
    ranker_bm = metapy.index.OkapiBM25(k1=1.5,b=0.75,k3=500)
    ev = metapy.index.IREval(cfg)

    with open(cfg, 'r') as fin:
        cfg_d = pytoml.load(fin)

    query_cfg = cfg_d['query-runner']
    if query_cfg is None:
        print("query-runner table needed in {}".format(cfg))
        sys.exit(1)

    start_time = time.time()
    top_k = 10
    query_path = query_cfg.get('query-path', 'queries.txt')
    query_start = query_cfg.get('query-id-start', 0)
    f1 = open("./bm25.avg_p.txt", "w")
    f2 = open("./inl2.avg_p.txt", "w")
    avg_in = []
    avg_bm = []
    query = metapy.index.Document()
    print('Running queries')
    with open(query_path) as query_file:
        for query_num, line in enumerate(query_file):
            query.content(line.strip())
            results = ranker_bm.score(idx, query, top_k)
            avg_p = ev.avg_p(results, query_start + query_num, top_k)
            avg_bm.append(avg_p)
            print("In query {} average precision: {}".format(query_num + 1, avg_p))
            f1.write (str(avg_p)+"\n")

            
            results = ranker_in.score(idx, query, top_k)
            avg_p = ev.avg_p(results, query_start + query_num, top_k)
            avg_in.append(avg_p)
            print("BM query {} average precision: {}".format(query_num + 1, avg_p))
            f2.write (str(avg_p)+"\n")
    f1.close()
    f2.close()
    print("Mean average precision: {}".format(ev.map()))
    print("Elapsed: {} seconds".format(round(time.time() - start_time, 4)))
    f = open("./significance.txt", "w")
    f.write (str(stats.ttest_rel(avg_bm, avg_in)[1]))
    f.close()

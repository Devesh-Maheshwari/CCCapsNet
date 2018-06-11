import os
import sys

from torchnlp.datasets.dataset import Dataset

from utils import GoogleDriveDownloader as gdd
from utils import text_preprocess


def imdb_dataset(directory='data/', data_type='imdb', preprocessing=False, fine_grained=False,
                 verbose=False, text_length=1200, share_id='1nlyc9HOTszLPcwzBtx3vws9b2K18eMxn'):
    """
    Load the IMDB dataset (Large Movie Review Dataset v1.0).

    This is a dataset for binary sentiment classification containing substantially more data than
    previous benchmark datasets. Provided a set of 25,000 highly polar movie reviews for training,
    and 25,000 for testing.
    After preprocessing, the total number of training samples is 1,399,272 and testing samples 59,969.
    The min length of text about train data is 4, max length is 1199, average length is 96; the min
    length of text about test data is 4, max length is 1199, average length is 96.

    **Reference:** http://ai.stanford.edu/~amaas/data/sentiment/

    Args:
        directory (str, optional): Directory to cache the dataset.
        data_type (str, optional): Which dataset to use.
        preprocessing (bool, optional): Whether to preprocess the original dataset. If preprocessing
            equals None, it will not download the preprocessed dataset, it will generate preprocessed
            dataset from the original dataset.
        fine_grained (bool, optional): Whether to use fine_grained dataset instead of polarity dataset.
        verbose (bool, optional): Whether to print the dataset details.
        text_length (int, optional): Only load the first text_length words, it only works when
            preprocessing is True.
        share_id (str, optional): Google Drive share ID about the original dataset to download.

    Returns:
        :class:`tuple` of :class:`torchnlp.datasets.Dataset`: Tuple with the training dataset and test
        dataset.

    Example:
        >>> train, test = imdb_dataset(preprocessing=True)
        >>> train[0:2]
        [{
          'label': 'pos',
          'text': 'movi respect lot memor quot list gem imagin movi joe piscopo funni funni...'},
         {
          'label': 'pos',
          'text': 'bizarr horror movi fill famou face stolen cristina rain flamingo road road...'}]
        >>> test[0:2]
        [{
          'label': 'pos',
          'text': 'movi respect lot memor quot list gem imagin movi joe piscopo funni funni...'},
         {
          'label': 'pos',
          'text': 'bizarr horror movi fill famou face stolen cristina rain flamingo road road...'}]
    """

    # other dataset have been set before, only imdb should be set here
    if preprocessing and data_type == 'imdb':
        share_id = ''

    if preprocessing:
        gdd.download_file_from_google_drive(share_id, data_type + '_preprocessed.zip', directory + data_type)
        if fine_grained:
            train_file, test_file = 'preprocessed_fine_grained_train.txt', 'preprocessed_fine_grained_test.txt'
        else:
            train_file, test_file = 'preprocessed_train.txt', 'preprocessed_test.txt'
    else:
        gdd.download_file_from_google_drive(share_id, data_type + '_orginal.zip', directory + data_type)
        if fine_grained:
            train_file, test_file = 'orginal_fine_grained_train.txt', 'orginal_fine_grained_test.txt'
        else:
            train_file, test_file = 'orginal_train.txt', 'orginal_test.txt'

    if verbose:
        min_train_length, avg_train_length, max_train_length = sys.maxsize, 0, 0
        min_test_length, avg_test_length, max_test_length = sys.maxsize, 0, 0

    ret = []
    for file_name in [train_file, test_file]:
        with open(os.path.join(directory, data_type, file_name), 'r', encoding='utf-8') as f:
            examples = []
            for line in f.readlines():
                label, text = line.split('\t')
                text = text.rstrip('\n')
                if preprocessing:
                    if len(text.split()) > text_length:
                        text = ' '.join(text.split()[:text_length])
                elif preprocessing is None:
                    text = text_preprocess(text)
                    if len(text.split()) == 0:
                        continue
                if verbose:
                    if file_name == train_file:
                        avg_train_length += len(text.split())
                        if len(text.split()) > max_train_length:
                            max_train_length = len(text.split())
                        if len(text.split()) < min_train_length:
                            min_train_length = len(text.split())
                    if file_name == test_file:
                        avg_test_length += len(text.split())
                        if len(text.split()) > max_test_length:
                            max_test_length = len(text.split())
                        if len(text.split()) < min_test_length:
                            min_test_length = len(text.split())
                examples.append({'label': label, 'text': text})
        ret.append(Dataset(examples))

    if verbose:
        print("[!] train length--(min: {}, avg: {}, max: {})".
              format(min_train_length, round(avg_train_length / len(ret[0])), max_train_length))
        print("[!] test length--(min: {}, avg: {}, max: {})".
              format(min_test_length, round(avg_test_length / len(ret[1])), max_test_length))
    return tuple(ret)


def agnews_dataset(directory='data/', preprocessing=False, verbose=False, text_length=1200):
    """
    Load the AG's News Topic Classification dataset (Version 3).

    The AG's news topic classification dataset is constructed by choosing 4 largest classes from
    the original corpus. Each class contains 30,000 training samples and 1,900 testing samples.
    The total number of training samples is 120,000 and testing 7,600.
    After preprocessing, the total number of training samples is 1,399,272 and testing samples 59,969.
    The min length of text about train data is 4, max length is 1199, average length is 96; the min
    length of text about test data is 4, max length is 1199, average length is 96.

    **Reference:** http://www.di.unipi.it/~gulli/AG_corpus_of_news_articles.html

    Example:
        >>> train, test = agnews_dataset(preprocessing=True)
        >>> train[0:2]
        [{
          'label': 'Business',
          'text': 'wall bear claw back black reuter reuter short seller wall street dwindl band...'},
         {
          'label': 'Business',
          'text': 'carlyl commerci aerospac reuter reuter privat invest firm carlyl group reput...'}]
        >>> test[0:2]
        [{
          'label': 'Business',
          'text': 'wall bear claw back black reuter reuter short seller wall street dwindl band...'},
         {
          'label': 'Business',
          'text': 'carlyl commerci aerospac reuter reuter privat invest firm carlyl group reput...'}]
    """

    share_id = '' if preprocessing else ''
    return imdb_dataset(directory, 'agnews', preprocessing, verbose=verbose, text_length=text_length, share_id=share_id)


def dbpedia_dataset(directory='data/', preprocessing=False, verbose=False, text_length=1200):
    """
    Load the DBPedia Ontology Classification dataset (Version 2).

    The DBpedia ontology classification dataset is constructed by picking 14 non-overlapping classes
    from DBpedia 2014. They are listed in classes.txt. From each of these 14 ontology classes, we
    randomly choose 40,000 training samples and 5,000 testing samples. Therefore, the total size
    of the training dataset is 560,000 and testing dataset 70,000.
    After preprocessing, the total number of training samples is 1,399,272 and testing samples 59,969.
    The min length of text about train data is 4, max length is 1199, average length is 96; the min
    length of text about test data is 4, max length is 1199, average length is 96.

    **Reference:** http://dbpedia.org

    Example:
        >>> train, test = dbpedia_dataset(preprocessing=True)
        >>> train[0:2]
        [{
          'label': 'Company',
          'text': 'abbott abbott farnham abbott limit british coachbuild busi base farnham base...'},
         {
          'label': 'Company',
          'text': 'schwan stabilo schwan stabilo german maker pen write colour cosmet marker...'}]
        >>> test[0:2]
        [{
          'label': 'Business',
          'text': 'wall bear claw back black reuter reuter short seller wall street dwindl band...'},
         {
          'label': 'Business',
          'text': 'carlyl commerci aerospac reuter reuter privat invest firm carlyl group reput...'}]
    """

    share_id = '' if preprocessing else ''
    return imdb_dataset(directory, 'dbpedia', preprocessing, verbose=verbose, text_length=text_length,
                        share_id=share_id)


def newsgroups_dataset(directory='data/', preprocessing=False, verbose=False, text_length=1200):
    """
    Load the 20 Newsgroups dataset (Version 'bydate').

    The 20 Newsgroups data set is a collection of approximately 20,000 newsgroup documents,
    partitioned (nearly) evenly across 20 different newsgroups. The total number of training
    samples is 11,293 and testing 7,527.
    After preprocessing, the total number of training samples is 1,399,272 and testing samples 59,969.
    The min length of text about train data is 4, max length is 1199, average length is 96; the min
    length of text about test data is 4, max length is 1199, average length is 96.

    **Reference:** http://qwone.com/~jason/20Newsgroups/

    Example:
        >>> train, test = newsgroups_dataset(preprocessing=True)
        >>> train[0:2]
        [{
          'label': 'alt.atheism',
          'text': 'alt atheism faq atheist resourc archiv name atheism resourc alt alt alt alt...'},
         {
          'label': 'alt.atheism',
          'text': 'alt atheism faq introduct atheism archiv name atheism introduct introduct...'}]
        >>> test[0:2]
        [{
          'label': 'Business',
          'text': 'wall bear claw back black reuter reuter short seller wall street dwindl band...'},
         {
          'label': 'Business',
          'text': 'carlyl commerci aerospac reuter reuter privat invest firm carlyl group reput...'}]
    """

    share_id = '' if preprocessing else ''
    return imdb_dataset(directory, 'newsgroups', preprocessing, verbose=verbose, text_length=text_length,
                        share_id=share_id)


def webkb_dataset(directory='data/', preprocessing=False, verbose=False, text_length=1200):
    """
    Load the World Wide Knowledge Base (Web->Kb) dataset (Version 1).

    The World Wide Knowledge Base (Web->Kb) dataset is collected by the World Wide Knowledge Base
    (Web->Kb) project of the CMU text learning group. These pages were collected from computer
    science departments of various universities in 1997, manually classified into seven different
    classes: student, faculty, staff, department, course, project, and other. The classes Department
    and Staff is discarded, because there were only a few pages from each university. The class Other
    is discarded, because pages were very different among this class. The total number of training
    samples is 2,785 and testing 1,383.
    After preprocessing, the total number of training samples is 1,399,272 and testing samples 59,969.
    The min length of text about train data is 4, max length is 1199, average length is 96; the min
    length of text about test data is 4, max length is 1199, average length is 96.

    **Reference:** http://www.cs.cmu.edu/afs/cs.cmu.edu/project/theo-20/www/data/

    Example:
        >>> train, test = webkb_dataset(preprocessing=True)
        >>> train[0:2]
        [{
          'label': 'student',
          'text': 'brian comput scienc depart univers wisconsin dayton street madison offic offic...'}
         {
          'label': 'student',
          'text': 'denni swanson web page mail pop uki offic hour comput lab offic anderson...'}]
        >>> test[0:2]
        [{
          'label': 'Business',
          'text': 'wall bear claw back black reuter reuter short seller wall street dwindl band...'},
         {
          'label': 'Business',
          'text': 'carlyl commerci aerospac reuter reuter privat invest firm carlyl group reput...'}]
    """

    share_id = '' if preprocessing else ''
    return imdb_dataset(directory, 'webkb', preprocessing, verbose=verbose, text_length=text_length, share_id=share_id)


def cade_dataset(directory='data/', preprocessing=False, verbose=False, text_length=1200):
    """
    Load the World Wide Knowledge Base (Web->Kb) dataset (Version 1).

    The World Wide Knowledge Base (Web->Kb) dataset is collected by the World Wide Knowledge Base
    (Web->Kb) project of the CMU text learning group. These pages were collected from computer
    science departments of various universities in 1997, manually classified into seven different
    classes: student, faculty, staff, department, course, project, and other. The classes Department
    and Staff is discarded, because there were only a few pages from each university. The class Other
    is discarded, because pages were very different among this class. The total number of training
    samples is 2,785 and testing 1,383.
    After preprocessing, the total number of training samples is 1,399,272 and testing samples 59,969.
    The min length of text about train data is 4, max length is 1199, average length is 96; the min
    length of text about test data is 4, max length is 1199, average length is 96.

    **Reference:** http://www.cs.cmu.edu/afs/cs.cmu.edu/project/theo-20/www/data/

    Example:
        >>> train, test = cade_dataset(preprocessing=True)
        >>> train[0:2]
        [{
          'label': 'student',
          'text': 'brian comput scienc depart univers wisconsin dayton street madison offic offic...'}
         {
          'label': 'student',
          'text': 'denni swanson web page mail pop uki offic hour comput lab offic anderson...'}]
        >>> test[0:2]
        [{
          'label': 'Business',
          'text': 'wall bear claw back black reuter reuter short seller wall street dwindl band...'},
         {
          'label': 'Business',
          'text': 'carlyl commerci aerospac reuter reuter privat invest firm carlyl group reput...'}]
    """

    share_id = '' if preprocessing else ''
    return imdb_dataset(directory, 'cade', preprocessing, verbose=verbose, text_length=text_length, share_id=share_id)


def sogou_dataset(directory='data/', preprocessing=False, verbose=False, text_length=1200):
    """
    Load the World Wide Knowledge Base (Web->Kb) dataset (Version 1).

    The World Wide Knowledge Base (Web->Kb) dataset is collected by the World Wide Knowledge Base
    (Web->Kb) project of the CMU text learning group. These pages were collected from computer
    science departments of various universities in 1997, manually classified into seven different
    classes: student, faculty, staff, department, course, project, and other. The classes Department
    and Staff is discarded, because there were only a few pages from each university. The class Other
    is discarded, because pages were very different among this class. The total number of training
    samples is 2,785 and testing 1,383.
    After preprocessing, the total number of training samples is 1,399,272 and testing samples 59,969.
    The min length of text about train data is 4, max length is 1199, average length is 96; the min
    length of text about test data is 4, max length is 1199, average length is 96.

    **Reference:** http://www.cs.cmu.edu/afs/cs.cmu.edu/project/theo-20/www/data/

    Example:
        >>> train, test = sogou_dataset(preprocessing=True)
        >>> train[0:2]
        [{
          'label': 'student',
          'text': 'brian comput scienc depart univers wisconsin dayton street madison offic offic...'}
         {
          'label': 'student',
          'text': 'denni swanson web page mail pop uki offic hour comput lab offic anderson...'}]
        >>> test[0:2]
        [{
          'label': 'Business',
          'text': 'wall bear claw back black reuter reuter short seller wall street dwindl band...'},
         {
          'label': 'Business',
          'text': 'carlyl commerci aerospac reuter reuter privat invest firm carlyl group reput...'}]
    """

    share_id = '' if preprocessing else ''
    return imdb_dataset(directory, 'sogou', preprocessing, verbose=verbose, text_length=text_length, share_id=share_id)


def yahoo_dataset(directory='data/', preprocessing=False, verbose=False, text_length=1200):
    """
    Load the Yahoo! Answers Topic Classification dataset (Version 2).

    The Yahoo! Answers topic classification dataset is constructed using 10 largest main categories.
    Each class contains 140,000 training samples and 6,000 testing samples. Therefore, the total number
    of training samples is 1,400,000 and testing samples 60,000 in this dataset.
    After preprocessing, the total number of training samples is 1,399,272 and testing samples 59,969.
    The min length of text about train data is 4, max length is 1199, average length is 96; the min
    length of text about test data is 4, max length is 1199, average length is 96.

    **Reference:** https://webscope.sandbox.yahoo.com/catalog.php?datatype=l

    Example:
        >>> train, test = yahoo_dataset(preprocessing=True)
        >>> train[0:2]
        [{
          'label': 'Computers & Internet',
          'text': 'doesn optic mous work glass tabl surfac optic mice led camera rapidli rapidli...'},
         {
          'label': 'Sports',
          'text': 'road motorcycl trail long distanc trail hear mojav road amaz nsearch onlin'}]
        >>> test[0:2]
        [{
          'label': 'Business',
          'text': 'wall bear claw back black reuter reuter short seller wall street dwindl band...'},
         {
          'label': 'Business',
          'text': 'carlyl commerci aerospac reuter reuter privat invest firm carlyl group reput...'}]
    """

    share_id = '' if preprocessing else ''
    return imdb_dataset(directory, 'yahoo', preprocessing, verbose=verbose, text_length=text_length, share_id=share_id)


def reuters_dataset(directory='data/', preprocessing=False, fine_grained=False, verbose=False, text_length=1200):
    """
    Load the Reuters-21578 R8 or Reuters-21578 R52 dataset (Version 'modApté').

    The Reuters-21578 dataset considers only the documents with a single topic and the classes
    which still have at least one train and one test example, we have 8 of the 10 most frequent
    classes and 52 of the original 90. In total there are 5,485 trainig samples and 2,189 testing
    samples in R8 dataset. The total number of training samples is 6,532 and testing 2,568 in R52
    dataset.
    After preprocessing, the total number of training samples is 1,399,272 and testing samples 59,969.
    The min length of text about train data is 4, max length is 1199, average length is 96; the min
    length of text about test data is 4, max length is 1199, average length is 96. (R8)
    After preprocessing, the total number of training samples is 1,399,272 and testing samples 59,969.
    The min length of text about train data is 4, max length is 1199, average length is 96; the min
    length of text about test data is 4, max length is 1199, average length is 96. (R52)

    **Reference:** http://www.daviddlewis.com/resources/testcollections/reuters21578/

    Example:
        >>> train, test = reuters_dataset(preprocessing=True)
        >>> train[0:2]
        [{
          'label': 'earn',
          'text': 'champion product approv stock split champion product inc board director...'}
         {
          'label': 'acq',
          'text': 'comput termin system cpml complet sale comput termin system inc complet...'}]
        >>> test[0:2]
        [{
          'label': 'Business',
          'text': 'wall bear claw back black reuter reuter short seller wall street dwindl band...'},
         {
          'label': 'Business',
          'text': 'carlyl commerci aerospac reuter reuter privat invest firm carlyl group reput...'}]
    """

    if fine_grained:
        share_id = '1JL83q8YoyaffLxSJsrJSAGYSDVcZotNR'
    else:
        share_id = '1jL06ZqR74fKYsMwAFwyGXE_KmZ_b1yGZ'
    return imdb_dataset(directory, 'reuters', preprocessing, fine_grained, verbose, text_length, share_id)


def yelp_dataset(directory='data/', preprocessing=False, fine_grained=False, verbose=False, text_length=1200):
    """
    Load the Yelp Review Full Star or Yelp Review Polarity dataset (Version 1).

    The Yelp reviews polarity dataset is constructed by considering stars 1 and 2 negative, and 3
    and 4 positive. For each polarity 280,000 training samples and 19,000 testing samples are take
    randomly. In total there are 560,000 training samples and 38,000 testing samples. Negative
    polarity is class 1, and positive class 2.
    The Yelp reviews full star dataset is constructed by randomly taking 130,000 training samples
    and 10,000 testing samples for each review star from 1 to 5. In total there are 650,000 training
    samples and 50,000 testing samples.
    After preprocessing, the total number of training samples is 1,399,272 and testing samples 59,969.
    The min length of text about train data is 4, max length is 1199, average length is 96; the min
    length of text about test data is 4, max length is 1199, average length is 96. (polarity)
    After preprocessing, the total number of training samples is 1,399,272 and testing samples 59,969.
    The min length of text about train data is 4, max length is 1199, average length is 96; the min
    length of text about test data is 4, max length is 1199, average length is 96. (full)

    **Reference:** http://www.yelp.com/dataset_challenge

    Example:
        >>> train, test = yelp_dataset(preprocessing=True)
        >>> train[0:2]
        [{
          'label': '1',
          'text': "frustrat goldberg patient repeat experi doctor nyc good doctor terribl staff..."}
         {
          'label': '2',
          'text': "goldberg year patient start mhmg great year big pictur gyn markoff found..."}]
        >>> test[0:2]
        [{
          'label': 'Business',
          'text': 'wall bear claw back black reuter reuter short seller wall street dwindl band...'},
         {
          'label': 'Business',
          'text': 'carlyl commerci aerospac reuter reuter privat invest firm carlyl group reput...'}]
    """

    if fine_grained:
        share_id = '1hRGkaOnYNtjhRXIm43Oo643GiStrxvJ0'
    else:
        share_id = '1twA4DhJ2mnWh2aQr0qK1UlgqKSmcxuZp'
    return imdb_dataset(directory, 'yelp', preprocessing, fine_grained, verbose, text_length, share_id)


def amazon_dataset(directory='data/', preprocessing=False, fine_grained=False, verbose=False, text_length=1200):
    """
    Load the Amazon Review Full Score or Amazon Review Polaridy dataset (Version 3).

    The Amazon reviews polarity dataset is constructed by taking review score 1 and 2 as negative,
    and 4 and 5 as positive. For each polarity 1,800,000 training samples and 200,000 testing samples
    are take randomly. In total there are 3,600,000 training samples and 400,000 testing samples.
    Negative polarity is class 1, and positive class 2.
    The Amazon reviews full score dataset is constructed by randomly taking 600,000 training samples
    and 130,000 testing samples for each review score from 1 to 5. In total there are 3,000,000
    training samples and 650,000 testing samples.
    After preprocessing, the total number of training samples is 1,399,272 and testing samples 59,969.
    The min length of text about train data is 4, max length is 1199, average length is 96; the min
    length of text about test data is 4, max length is 1199, average length is 96. (polarity)
    After preprocessing, the total number of training samples is 1,399,272 and testing samples 59,969.
    The min length of text about train data is 4, max length is 1199, average length is 96; the min
    length of text about test data is 4, max length is 1199, average length is 96. (full)

    **Reference:** http://jmcauley.ucsd.edu/data/amazon/

    Example:
        >>> train, test = amazon_dataset(preprocessing=True)
        >>> train[0:2]
        [{
          'label': '2',
          'text': 'stune gamer sound track beauti paint seneri mind recomend peopl hate vid...'}
         {
          'label': '2',
          'text': 'soundtrack read lot review game soundtrack figur write review disagre bit...'}]
        >>> test[0:2]
        [{
          'label': 'Business',
          'text': 'wall bear claw back black reuter reuter short seller wall street dwindl band...'},
         {
          'label': 'Business',
          'text': 'carlyl commerci aerospac reuter reuter privat invest firm carlyl group reput...'}]
    """

    if fine_grained:
        share_id = '1IegvAdxzTye3XLybtfUD1UgNtDzVXn3y'
    else:
        share_id = '1Wxahg6ipC9OFnzGH901S6NIVYNILS0ND'
    return imdb_dataset(directory, 'amazon', preprocessing, fine_grained, verbose, text_length, share_id)

# -------------------------------------------------------
# Assignment 2
# Written by:
#   Paul Piggott (27519451)
#   Louis Madre  (40087452)
#   Davy Riviere (29379355)
# For COMP 472 Section AA – Summer 2021
# --------------------------------------------------------

from nlp.scraping.api import ImdbApi
from nlp.scraping.review_parser import ReviewParser
from nlp.pipeline.dataset import DataSet
from nlp.pipeline.bayes import NaiveBayesClassifier
from nlp.pipeline.frequency import FrequencyIterator
from nlp.pipeline.delta import DeltaIterator
from nlp.pipeline.word_length import WordLengthIterator

import matplotlib.pyplot as plt

task2_X = None
task2_y = None


def main():
    global task2_X, task2_y
    # Keeping Up With The Kardashians   tt1086761
    # Westworld   tt0475784
    # Mr Robot tt4158110
    # Game of Thrones tt0944947
    # The Sopranos tt0141842
    # Modern Family tt1442437
    # H F-O tt1600194
    # Grey's Anatomy   tt0413573
    # Supernatural  tt0460681
    parser = ReviewParser(show_id='tt4158110')
    parser.scrape()
    # print('\n\n\nCSV OUTPUT::\n\n')
    parser.episodes.to_csv()
    dataset = DataSet(parser.reviews)
    X, y = dataset.train_test_split()
    print()
    task2_X = X.copy()  # making copies of X, y which are local to main() into task2_X, y
    task2_y = y.copy()  # so we can refer back to them later, outside of driver.py
    nbc = NaiveBayesClassifier(training_data=X)
    nbc.train()
    nbc.export_training_data()
    preds = nbc.predict(y)
    nbc.validate(preds, y)
    nbc.export_predictions(preds, y)


if __name__ == '__main__':
    print('\nRunning Task 1:\n')
    main()
    print('\nTask 1 complete. Files saved for: remove.txt, model.txt and result.txt.\n')

    print('Running Task 2:\n')
    user_input = ''
    while user_input != '##':
        user_input = input('Which task would you like to run?\nEnter 2.1, 2.2, 2.3, or ## to exit: ')
        if user_input == '2.1':
            # generate an object that trains the model on 7 iterations (using different word frequencies)
            frq = FrequencyIterator(task2_X, task2_y)
            # perform the iterations
            frq.iterate()
        elif user_input == '2.2':
            # generate an object that trains the model on 6 iterations (using different delta values)
            dn = DeltaIterator(task2_X, task2_y)
            # perform the iterations
            dn.iterate()
        elif user_input == '2.3':
            # generate an object that trains the model on 4 iterations (using different word lengths)
            wrdln = WordLengthIterator(task2_X, task2_y)
            # perform the iterations
            wrdln.iterate()
        elif user_input == '##':
            break
        else:
            print('\nTry again.')

    print('\nProgram will now terminate. Good bye.')

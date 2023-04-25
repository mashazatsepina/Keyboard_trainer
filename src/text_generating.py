import random
from src.russian_words import russian_words_list

def text_generate(gen_size = 100) -> str:
    """ Generating a string of random words """
    text = [random.choice(russian_words_list) for _ in range(gen_size)]
    return ' '.join(text)
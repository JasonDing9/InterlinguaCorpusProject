# Interlingua Corpus 

More information: http://www.interlinguacorpus.org/

Interlingua (ISO 639 language codes ia, ina) is a naturalistic planned Italic international auxiliary language (IAL), developed between 1937 and 1951 by the International Auxiliary Language Association (IALA). Its vocabulary and grammar are derived from a wide range of western European natural languages. Interlingua was developed to combine a simple, mostly regular grammar with a vocabulary common to English, French, Italian, Spanish and Portuguese. These characteristics make it especially easy to learn for those whose native languages were sources of Interlingua's vocabulary and grammar. Interlingua can also be used as a rapid introduction to many natural languages. Written Interlingua is largely comprehensible to the hundreds of millions of people who speak Romance languages.

The goal of the Interlingua Corpus Project is to aggregate a large collection of Interlingua sentences as a community resource. The sentences in this corpus, including matched pairs of Interlingua-English sentences, are automatically collected from public websites and documents using a web crawler. The emphasis of this project is on sentences because sentences provide vocabulary in context and represent the grammar as used in various styles of writing. This collection of Interlingua sentences will provide a foundation for a variety of uses including enumeration of Interlingua's core vocabulary and development of comprehensive frequency dictionaries for language learners, corpus linguistics studies, and for the development of computational linguistics resources such as language models and machine translation tools for Interlingua.

Interlingua Corpus Release 1.0: COMING SOON<br />
Release Notes<br />
Interlingua Sentences<br />
Interlingua Word Frequency List<br />
Interlingua-English Parallel Sentences<br />
Please email interlinguacorpus@gmail.com for questions and suggestions.

# How to use the Python Files

The main Python file to run is main.py. There are files missing such as a language model, but there is explanations for each functions. In order to use the web crawler, use the function crawler. In order to use the parallel sentence extracter, use the function parallel_sentences_extractor. For examples on how to start each script, look in the crawler folder for an example of the web crawler and 4_bibles for an example of the parallel_setences_extractor.

Note: The language model 8_lang_50k_model.bin is not included.

The other notable python files are:

QC_INA_sentences.py - Does a quick quality control of the extracted interlingua sentences.<br />
removeBad.py (in 4_bibles) - Does a quality control of the extracted parallel sentences.<br />


# Mental Health Keywords for Twitter

This repository contains a list of keywords curated to detect mentions of mental health issues on Twitter. The list is curated to go beyond standard disorder mentions and instead highlight terms and phrases that may be indicative of mental distress.


As of June 15, 2020, the keywords contained in this repository are at Version 1. We plan to update these terms/phrases (i.e. remove low-frequency, low-precision, add missing) as data is captured from an ongoing Twitter stream. We note that Twitter limits keyword-based stream captures to 400 terms at a time. This final list is stored in mental_health_keywords_400.txt

## Resources

Code in this repository was used to filter, compile some of the keyword lists. However, the actual identification/ranking of term/phrase importance was done in this repository: https://github.com/kharrigian/mental-health

## Construction

This list of terms was constructed using a combination of automatic and manual methods. We describe the procedure below.

1. Retrieve Tweet data from "Multi-Task Learning for Mental Health using Social Media Text" (Benton et al., 2017). This dataset contains user-level annotations of 10 mental health conditions--Anxiety, Bipolar Disorder, Borderline Personality Disorder, Depression, Eating Disorder, Panic Disorder, PTSD, Schizophrenia, Suicidal Ideation, Suicide Attempt. Access to the dataset requires a signed data usage agreement and IRB approval.

2. In the full dataset, there are minor temporal differences between classes. For example, the depression sample starts earlier and ends later than the control sample. Accordingly, we truncate each condition's time window in which tweets are considered. All conditions are provided with a maximum allowed date of 2016-01-01. The start dates are as follows:

* Anxiety: 2010-01-01
* Bipolar: 2011-01-01
* Borderline: 2013-01-01
* Depression: 2010-01-01
* Eating: 2011-01-01
* Panic: 2011-01-01
* PTSD: 2011-01-01
* Schizophrenia: 2012-01-01
* Suicidal Ideation: 2013-01-01
* Suicide Attempt: 2010-01-01

3. All tweets are tokenized using the tokenization procedure described in the mental health repository listed above. We use the following parameters for learning vocabularies within each dataset. 

```
## Vocabulary Parameters
VOCAB_PARAMS = {
    "filter_negate":True,
    "filter_upper":True,
    "filter_punctuation":True,
    "filter_numeric":True,
    "filter_url":True,
    "filter_retweet":True,
    "filter_stopwords":False,
    "keep_pronouns":True,
    "filter_user_mentions":True,
    "preserve_case":False,
    "emoji_handling":"strip",
    "max_vocab_size":None,
    "min_token_freq":10,
    "max_tokens_per_document":None,
    "max_documents_per_user":None,
    "binarize_counter":True,
    "filter_mh_subreddits":"all",
    "filter_mh_terms":"smhd",
    "keep_retweets":False,
    "random_state":42,
}
```

4. For each condition y, we compute Pointwise Mutual Information log(p(x|y) / p(x)) of all n-grams x. We process each size of n-grams (n=[1,4]) separately.

5. For each feature ranking, we identify the top 250 terms with the highest PMI score relative to the positive class. When ranking, we only consider terms that appear in at least 30 user's tweet histories. These ranked results are stored in `./raw/` as newline-delimited .txt files.

6. While many n-grams were deemed relevant for mental-health status detection in our historical datasets, we wanted to curate a list that was relatively interpretable and less likely to identify false positives. Moreover, Twitter limits keyword lists to 400 terms when examining a stream of tweets. Accordingly, we perform manual filtering of each n-gram list, removing terms that are not immediately interpretable as being related to a mental-health condition. We acknowledge that our criteria for filtering is relatively subjective. Results of the filtering are stored in `./filtered/`.

7. Filtered keyword lists are combined using code in `compile_lists.py` and stored in `combined_keywords.csv`. We append keywords from the union of the RSDD (Yates et al., 2017) and SMHD (Cohan et al., 2018) keyword lists. Posts matching these terms were excluded during the initial PMI calculation so that we could highlight non-trivial keywords/phrases. We remove any keywords/phrases who have a substring elsewhere in the keyword list (i.e. "kill myself today" and "kill myself" only maintains "kill myself").

8. Finally, to meet Twitter's 400-term limit. We perform one-additional round of manual filtering in the `combined_keywords.csv` file. The result is found in `combined_keywords_manual_selection.csv`.

* Right away, we mark the bottom 240 n-grams based on their relative rank within the individual lists.
* We also ignore common misspellings of disorders listed in the RSDD/SMHD sets.
* We opt to ignore any terms related to gender identity and sexuality. While this discussion is often seen in people living with a mental health disorder, it is the not the primary objective in this list.
* We also make the decision to filter out terms specifically related to eating disorders (e.g. count calories) as they tend to be their own breed of mental health disorders.
* We ignore n-grams that are likely to be used in discussion about Coronavirus as opposed to mental-health disorders (e.g. "death", "crisis", "hospital").
* We ignore words that are more likely to be ambiguous (e.g. "the army", "navy"). These are likely to be important in i.e. PTSD detection, but will also lead to several false positives.
* We ignore phrases that are subjectively more likely to be used in discussion not about mental health (e.g. "i stan", "god dammit").   

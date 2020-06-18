
##################
### Imports
##################

## Imports
import json
from glob import glob
import pandas as pd

##################
### Helpers
##################

## File Parsing
def parse_file(filename):
    """

    """
    ## Metadata
    dataset = "clpsych" if "clpsych" in filename else "multitask"
    disorder = filename.split(f"{dataset}_")[1].split("_n")[0]
    ngram = int(filename.split(".txt")[0].split("_n")[-1])
    ## Load Filtered Data
    keywords = [i.strip() for i in open(filename, "r").readlines()]
    ## Load Original Data, Rank
    unfiltered_keywords = [i.strip() for i in open(filename.replace("filtered","raw"), "r").readlines()]
    ranks = dict(zip(unfiltered_keywords, range(len(unfiltered_keywords))))
    keyword_ranks = [ranks[k] for k in keywords]
    return dataset, disorder, ngram, keywords, keyword_ranks

def is_subset(sl,
              l):
    """
    Find lists within lists
    Args:
        sl (list): List to look for
        l (list): Large list of items to search within
    
    Returns:
        results (list): Start, end indice spans of matches
    """
    sll = len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            return True
    return False

##################
### Load Data
##################

## Load Manually-filtered Keywords
filtered_data = []
for filename in glob("./filtered/*txt"):
    ds, dis, n, keywords, ranks = parse_file(filename)
    df = pd.DataFrame(keywords,columns=["ngram"])
    df["dataset"] = ds
    df["disorder"] = dis
    df["relative_rank"] = ranks
    filtered_data.append(df)
filtered_data = pd.concat(filtered_data).reset_index(drop=True)

##################
### Load Reddit Lists
##################

## Load Terms
with open("./resources/mh_terms.json","r") as the_file:
    mh_terms = json.load(the_file)

## Combine
external_terms = mh_terms["expansions"]["_condition"]
external_terms.extend(mh_terms["terms"]["rsdd"])
external_terms.extend(mh_terms["terms"]["smhd"])
external_terms = sorted(set(external_terms))

## Format
external_terms =  pd.DataFrame(external_terms,columns=["ngram"])
external_terms["dataset"] = "reddit"
external_terms["disorder"] = "general"
external_terms["relative_rank"] = 0

## Add
filtered_data = filtered_data.append(external_terms).reset_index(drop=True)

##################
### Pre-format
##################

## Clean Terms
filtered_data["ngram"] = filtered_data["ngram"].str.replace("_"," ")

## Add N-Gram Flag
filtered_data["n"] = filtered_data["ngram"].str.split().map(len)

## N-Gram to Metadata Map
ngram_disorder_map = filtered_data.groupby("ngram")["disorder"].unique().to_dict()
ngram_dataset_map = filtered_data.groupby("ngram")["dataset"].unique().to_dict()
ngram_rank_map = filtered_data.groupby("ngram")["relative_rank"].min().map(lambda i: [i]).to_dict()
ngram_occurrence_map = filtered_data.groupby("ngram").size().map(lambda i: [i]).to_dict()

##################
### De-duplicate
##################

## Identify Sub-string
terms = list(map(lambda i: i.split(), sorted(filtered_data["ngram"].unique(), key=lambda x: len(x))))
outer_strings = {}
for t1, tm1 in enumerate(terms):
    for tm2 in terms[t1+1:]:
        if is_subset(tm1, tm2) or " ".join(tm1) in " ".join(tm2):
            if tuple(tm2) not in outer_strings:
                outer_strings[tuple(tm2)] = []
            outer_strings[tuple(tm2)].append(tuple(tm1))

## Identify Reverse Mapping
inner_strings = {}
for outer, outer_matches in outer_strings.items():
    for om in outer_matches:
        if " ".join(om) not in inner_strings:
            inner_strings[" ".join(om)] = []
        inner_strings[" ".join(om)].append(" ".join(outer))

## Isolate Sub-strings
filtered_terms = [" ".join(t) for t in terms if tuple(t) not in outer_strings]

##################
### Format DataFrame
##################

def get_meta(ngram, meta_dict):
    """

    """
    meta = list(meta_dict[ngram])
    if ngram in inner_strings:
        for outer in inner_strings[ngram]:
            meta.extend(meta_dict[ngram])
    meta = sorted(set(meta))
    return meta

## Create Filtered Data Set
filtered_data = filtered_data.loc[filtered_data["ngram"].isin(set(filtered_terms))].drop_duplicates("ngram",keep="first")
filtered_data["dataset"] = filtered_data["ngram"].map(lambda i: get_meta(i, ngram_dataset_map))
filtered_data["disorder"] = filtered_data["ngram"].map(lambda i: get_meta(i, ngram_disorder_map))
filtered_data["relative_rank"] = filtered_data["ngram"].map(lambda i: min(get_meta(i, ngram_rank_map)))
filtered_data["count"] = filtered_data["ngram"].map(lambda i: sum(get_meta(i, ngram_occurrence_map)))

## Clean Up
filtered_data = filtered_data.sort_values("relative_rank",ascending=True).reset_index(drop=True)
filtered_data.rename(columns={"relative_rank":"min_relative_rank"},inplace=True)
for col in ["dataset","disorder"]:
    filtered_data[col] = filtered_data[col].map(lambda i: "-".join(sorted(i)))

##################
### Dump
##################

## Dump
filtered_data.to_csv("combined_keywords.csv",index=False)
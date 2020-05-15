import os
from transformers import pipeline

pipeline_name = os.getenv("PIPELINE", "sentiment-analysis")

MAX_LEN = int(os.getenv('MAX_LEN', '0'))

nlp = pipeline(pipeline_name)


def predictor(in_lines, batch_size=4):
    # For sentiment analysic, hugging face transformers throws error when batch_size > 2
    # https://github.com/huggingface/transformers/issues/2941

    if MAX_LEN:
        in_lines = [l[:MAX_LEN] for l in in_lines]
    
    pad = False
    if pipeline_name in {"sentiment-analysis"}:
        pad = True
        batch_size = min(batch_size, 2)

    preds = []
    while in_lines:
        if pad:
            pred = nlp(in_lines[:batch_size], pad_to_max_length=pad)
        else:
            pred = nlp(in_lines[:batch_size])

        if len(in_lines[:batch_size]) == 1 and pipeline_name in {"ner"}:
            pred = [pred]

        preds += pred

        in_lines = in_lines[batch_size:]

    if pipeline_name == "sentiment-analysis":
        for i, pred in enumerate(preds):
            preds[i]["score"] = float(pred["score"])

    elif pipeline_name == "ner":
        if isinstance(preds[0], dict):
            preds = [preds]

        for i, pred in enumerate(preds):
            for j, ent in enumerate(pred):
                preds[i][j]["score"] = float(ent["score"])

    return preds


if __name__ == "__main__":
    example = [
        "We are very happy to include pipeline into the transformers repository. My name is John Smith. We are very happy to include pipeline into the transformers repository. My name is John Smith. We are very happy to include pipeline into the transformers repository. My name is John Smith. We are very happy to include pipeline into the transformers repository. My name is John Smith. We are very happy to include pipeline into the transformers repository. My name is John Smith. We are very happy to include pipeline into the transformers repository. My name is John Smith. We are very happy to include pipeline into the transformers repository. My name is John Smith."
    ]

    import json
    import pickle

    print(json.dumps(predictor(example)))

    pickle.dump(example, open("example.pkl", "wb"), protocol=2)

# backend/scripts/evaluation/evaluation_all.py

import os
import time
import json
import pandas as pd
from dotenv import load_dotenv

# ----------------------------
# External Libraries
# ----------------------------
from openai import OpenAI
from anthropic import Anthropic

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from sklearn.metrics import (
    accuracy_score, f1_score, precision_score,
    recall_score, classification_report
)

from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification, AutoConfig
)
from kobert_transformers import get_tokenizer, get_kobert_model


# =============================================================
# ?òÍ≤Ω Î≥Ä??
# =============================================================
load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# =============================================================
# ?åÏä§???∞Ïù¥??Î°úÎìú
# =============================================================
TEST_PATH = "backend/data/all_test.csv"
test_df = pd.read_csv(TEST_PATH)

label_list = sorted(test_df["label"].unique())
label2id = {lab: i for i, lab in enumerate(label_list)}
id2label = {i: lab for lab, i in label2id.items()}


# =============================================================
# Dataset Class
# =============================================================
class FacilityDataset(Dataset):
    def __init__(self, df, tokenizer, label2id, max_len=64):
        self.texts = df["text"].astype(str).tolist()
        self.labels = df["label"].map(label2id).astype(int).tolist()
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self): 
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.texts[idx],
            truncation=True, padding="max_length",
            max_length=self.max_len, return_tensors="pt"
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels": torch.tensor(self.labels[idx])
        }


# =============================================================
# Î∂ÑÎ•ò Î™®Îç∏ ?âÍ? (HuggingFace)
# =============================================================
def evaluate_hf(model, loader, device):
    model.eval()
    preds, trues = [], []

    with torch.no_grad():
        for batch in loader:
            outs = model(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device)
            )

            logits = outs.logits if hasattr(outs, "logits") else outs[0]
            pred = logits.argmax(dim=1).cpu().numpy()

            preds.extend(pred)
            trues.extend(batch["labels"].cpu().numpy())

    return preds, trues


# =============================================================
# KoBERT ?âÍ?
# =============================================================
def evaluate_kobert(bert, classifier, loader, device):
    bert.eval()
    classifier.eval()
    preds, trues = [], []

    with torch.no_grad():
        for batch in loader:
            ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            labels = batch["labels"]

            outputs = bert(input_ids=ids, attention_mask=mask)
            pooled = outputs.pooler_output
            logits = classifier(pooled)

            pred = torch.argmax(logits, dim=1).cpu().numpy()

            preds.extend(pred)
            trues.extend(labels.numpy())

    return preds, trues


# =============================================================
# LLM ?âÍ?
# =============================================================
LLM_QUESTIONS = [
    "Íµ¨Î¶¨??Í∑ºÏ≤ò 5???¥Ìïò ?ÑÌåå??Ï∂îÏ≤ú?¥Ï§ò",
    "Ï¥àÎì±?ôÍµê Í∞ÄÍπåÏö¥ ?ÑÌåå???åÎ†§Ï§?,
    "Ï°∞Ïö©?òÍ≥† ?πÏ?Í∞Ä ÎßéÏ? ?ÑÌåå??Ï∂îÏ≤ú?¥Ï§ò"
]

REQUIRED_KEYS = {"budget", "location", "conditions"}


def extract_json(text):
    try:
        return json.loads(text)
    except:
        return None


def call_llm(model_name, question):
    try:
        if model_name == "gpt-4.1-mini":
            res = openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": question}],
                max_tokens=200
            )
            return extract_json(res.choices[0].message.content)

        if model_name == "Claude-3":
            res = claude_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=200,
                messages=[{"role": "user", "content": question}],
            )
            return extract_json(res.content[0].text)


    except Exception as e:
        print(f"[LLM ERROR] {model_name}: {e}")
        return None


def evaluate_llm(model_name):
    success = 0
    speeds = []
    outputs = []

    print(f"\n??{model_name} ?âÍ? ?úÏûë")

    for q in LLM_QUESTIONS:
        start = time.time()
        out = call_llm(model_name, q)
        end = time.time()

        outputs.append(out)
        speeds.append(end - start)

        if out and isinstance(out, dict) and REQUIRED_KEYS.issubset(out.keys()):
            success += 1

    accuracy = success / len(LLM_QUESTIONS)
    speed = sum(speeds) / len(speeds)

    key_sets = [tuple(sorted(o.keys())) for o in outputs if isinstance(o, dict)]
    consistency = 1.0 if len(set(key_sets)) == 1 else 0.5

    return {
        "model": model_name,
        "accuracy": accuracy,
        "speed": speed,
        "consistency": consistency
    }


# =============================================================
# ?ÑÏ≤¥ ?âÍ? ?§Ìñâ
# =============================================================
def main():
    print("\n=======================================")
    print("?î• ?ÑÏ≤¥ Î™®Îç∏ ?µÌï© ?âÍ? ?úÏûë")
    print("=======================================\n")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    CLASSIFIER_RESULTS = {}

    # ---------------------------------------------------------
    # 1) ELECTRA ??FIXED num_labels mismatch
    # ---------------------------------------------------------
    print("\n============ ELECTRA ?âÍ? ============\n")

    ele_tok = AutoTokenizer.from_pretrained("monologg/koelectra-small-v3-discriminator")
    ele_loader = DataLoader(FacilityDataset(test_df, ele_tok, label2id), batch_size=16)

    ele_config = AutoConfig.from_pretrained("monologg/koelectra-small-v3-discriminator")
    ele_config.num_labels = len(label_list)
    ele_config.return_dict = True

    ele_model = AutoModelForSequenceClassification.from_pretrained(
        "monologg/koelectra-small-v3-discriminator",
        config=ele_config
    )

    ele_model.load_state_dict(torch.load("backend/models/electra_all_classifier.pt", map_location=device))
    ele_model.to(device)

    ele_preds, ele_trues = evaluate_hf(ele_model, ele_loader, device)

    CLASSIFIER_RESULTS["ELECTRA"] = {
        "accuracy": accuracy_score(ele_trues, ele_preds),
        "precision": precision_score(ele_trues, ele_preds, average="macro"),
        "recall": recall_score(ele_trues, ele_preds, average="macro"),
        "f1": f1_score(ele_trues, ele_preds, average="macro"),
    }

    print(classification_report(ele_trues, ele_preds, target_names=label_list))


    # ---------------------------------------------------------
    # 2) KLUE RoBERTa
    # ---------------------------------------------------------
    print("\n============ KLUE ?âÍ? ============\n")

    klu_tok = AutoTokenizer.from_pretrained("klue/roberta-small")
    klu_loader = DataLoader(FacilityDataset(test_df, klu_tok, label2id), batch_size=16)

    klu_config = AutoConfig.from_pretrained("klue/roberta-small")
    klu_config.num_labels = len(label_list)
    klu_config.return_dict = True

    klu_model = AutoModelForSequenceClassification.from_pretrained(
        "klue/roberta-small",
        config=klu_config
    )
    klu_model.load_state_dict(torch.load("backend/models/klue_all_classifier.pt", map_location=device))
    klu_model.to(device)

    klu_preds, klu_trues = evaluate_hf(klu_model, klu_loader, device)

    CLASSIFIER_RESULTS["KLUE"] = {
        "accuracy": accuracy_score(klu_trues, klu_preds),
        "precision": precision_score(klu_trues, klu_preds, average="macro"),
        "recall": recall_score(klu_trues, klu_preds, average="macro"),
        "f1": f1_score(klu_trues, klu_preds, average="macro"),
    }

    print(classification_report(klu_trues, klu_preds, target_names=label_list))


    # ---------------------------------------------------------
    # 3) KoBERT
    # ---------------------------------------------------------
    print("\n============ KoBERT ?âÍ? ============\n")

    kob_tok = get_tokenizer()
    kob_loader = DataLoader(FacilityDataset(test_df, kob_tok, label2id), batch_size=16)

    bert = get_kobert_model()
    classifier = nn.Linear(768, len(label_list))

    saved = torch.load("backend/models/kobert_all_classifier.pt", map_location=device)
    bert.load_state_dict(saved["kobert"])
    classifier.load_state_dict(saved["classifier"])
    bert.to(device)
    classifier.to(device)

    kob_preds, kob_trues = evaluate_kobert(bert, classifier, kob_loader, device)

    CLASSIFIER_RESULTS["KoBERT"] = {
        "accuracy": accuracy_score(kob_trues, kob_preds),
        "precision": precision_score(kob_trues, kob_preds, average="macro"),
        "recall": recall_score(kob_trues, kob_preds, average="macro"),
        "f1": f1_score(kob_trues, kob_preds, average="macro"),
    }

    print(classification_report(kob_trues, kob_preds, target_names=label_list))


    # ---------------------------------------------------------
    # ?±Îä• ÎπÑÍµê??
    # ---------------------------------------------------------
    print("\n==============================")
    print("?ìä Î™®Îç∏ ?±Îä• ÎπÑÍµê??(Accuracy / F1)")
    print("==============================\n")

    df = pd.DataFrame(CLASSIFIER_RESULTS).T
    print(df)

    best_model = df.sort_values("f1", ascending=False).index[0]
    print(f"\n?éØ ÏµúÏ¢Ö ?†ÌÉù??Î™®Îç∏: {best_model} (F1-score Í∏∞Ï?)")


    # ---------------------------------------------------------
    # LLM JSON ?åÏÑú ?âÍ?
    # ---------------------------------------------------------
    print("\n==============================")
    print("?§ñ LLM JSON ?åÏÑú ?âÍ?")
    print("==============================\n")

    gpt_res = evaluate_llm("gpt-4.1-mini")
    claude_res = evaluate_llm("Claude-3")

    llm_df = pd.DataFrame([gpt_res, claude_res])
    print(llm_df)

    print("\n?éâ ?ÑÏ≤¥ ?âÍ? ?ÑÎ£å!")


if __name__ == "__main__":
    main()

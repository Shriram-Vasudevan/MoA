## Prompt gsm8k-1

**Question:** Liam reads 12 pages a day. After 5 days, how many pages has he read?

### Single Model Baseline

❌ **Orion-Strong sample** → **55**

```
Quick intuition on: Liam reads 12 pages a day. After 5 days, how many pages has he read?
A faster mental calculation suggests the answer is 55, even if not every step is fully justified.
Final Answer: 55
```

### Mixed-MoA Aggregation

❌ **Mixed-MoA (majority)** → **50**

Mixed-MoA (majority) selected '50' with vote distribution [50: 2, 55: 1]. Supporting samples: Nova-Medium#0, Atlas-Weak#0.

| Model Sample | Final Answer | Confidence |
| --- | --- | --- |
| Orion-Strong#0 | 55 | 0.43 |
| Nova-Medium#0 | 50 | 0.36 |
| Atlas-Weak#0 | 50 | 0.31 |

### Self-MoA Aggregation

✅ **Self-MoA (majority)** → **60**

Self-MoA (majority) selected '60' with vote distribution [60: 3, 55: 1]. Supporting samples: Orion-Strong#1, Orion-Strong#2, Orion-Strong#3.

| Model Sample | Final Answer | Confidence |
| --- | --- | --- |
| Orion-Strong#0 | 55 | 0.43 |
| Orion-Strong#1 | 60 | 0.89 |
| Orion-Strong#2 | 60 | 0.89 |
| Orion-Strong#3 | 60 | 0.89 |

### Self-MoA-Seq Aggregation

✅ **Self-MoA-Seq (window=2)** → **60**

Self-MoA-Seq (window=2) selected '60' with vote distribution [60: 3, 55: 1]. Supporting samples: Orion-Strong#1, Orion-Strong#2, Orion-Strong#3. Processed in 2 sliding windows of size 2.

## Prompt gsm8k-2

**Question:** A recipe needs 3 eggs per cake. How many eggs are needed for 4 cakes?

### Single Model Baseline

✅ **Orion-Strong sample** → **12**

```
Considering the question: A recipe needs 3 eggs per cake. How many eggs are needed for 4 cakes?
Break it into steps, compute carefully, and verify the result.
Double-checking gives 12, which matches all constraints.
Final Answer: 12
```

### Mixed-MoA Aggregation

✅ **Mixed-MoA (majority)** → **12**

Mixed-MoA (majority) selected '12' with vote distribution [12: 1, 9: 1, 16: 1]. Supporting samples: Orion-Strong#0.

| Model Sample | Final Answer | Confidence |
| --- | --- | --- |
| Orion-Strong#0 | 12 | 0.89 |
| Nova-Medium#0 | 9 | 0.36 |
| Atlas-Weak#0 | 16 | 0.31 |

### Self-MoA Aggregation

✅ **Self-MoA (majority)** → **12**

Self-MoA (majority) selected '12' with vote distribution [12: 4]. Supporting samples: Orion-Strong#0, Orion-Strong#1, Orion-Strong#2, Orion-Strong#3.

| Model Sample | Final Answer | Confidence |
| --- | --- | --- |
| Orion-Strong#0 | 12 | 0.89 |
| Orion-Strong#1 | 12 | 0.89 |
| Orion-Strong#2 | 12 | 0.89 |
| Orion-Strong#3 | 12 | 0.89 |

### Self-MoA-Seq Aggregation

✅ **Self-MoA-Seq (window=2)** → **12**

Self-MoA-Seq (window=2) selected '12' with vote distribution [12: 4]. Supporting samples: Orion-Strong#0, Orion-Strong#1, Orion-Strong#2, Orion-Strong#3. Processed in 2 sliding windows of size 2.

## Prompt gsm8k-3

**Question:** Sara saves $5 each week. After 7 weeks, how much has she saved?

### Single Model Baseline

❌ **Orion-Strong sample** → **30**

```
Quick intuition on: Sara saves $5 each week. After 7 weeks, how much has she saved?
A faster mental calculation suggests the answer is 30, even if not every step is fully justified.
Final Answer: 30
```

### Mixed-MoA Aggregation

❌ **Mixed-MoA (majority)** → **30**

Mixed-MoA (majority) selected '30' with vote distribution [30: 2, 28: 1]. Supporting samples: Orion-Strong#0, Atlas-Weak#0.

| Model Sample | Final Answer | Confidence |
| --- | --- | --- |
| Orion-Strong#0 | 30 | 0.43 |
| Nova-Medium#0 | 28 | 0.36 |
| Atlas-Weak#0 | 30 | 0.31 |

### Self-MoA Aggregation

✅ **Self-MoA (majority)** → **35**

Self-MoA (majority) selected '35' with vote distribution [35: 3, 30: 1]. Supporting samples: Orion-Strong#1, Orion-Strong#2, Orion-Strong#3.

| Model Sample | Final Answer | Confidence |
| --- | --- | --- |
| Orion-Strong#0 | 30 | 0.43 |
| Orion-Strong#1 | 35 | 0.89 |
| Orion-Strong#2 | 35 | 0.89 |
| Orion-Strong#3 | 35 | 0.89 |

### Self-MoA-Seq Aggregation

✅ **Self-MoA-Seq (window=2)** → **35**

Self-MoA-Seq (window=2) selected '35' with vote distribution [35: 3, 30: 1]. Supporting samples: Orion-Strong#1, Orion-Strong#2, Orion-Strong#3. Processed in 2 sliding windows of size 2.

---

## Aggregate Accuracy

| Strategy | Accuracy | Correct / Total |
| --- | --- | --- |
| Single Strong Sample | 0.33 | 1 / 3 |
| Mixed-MoA (majority) | 0.33 | 1 / 3 |
| Self-MoA (majority) | 1.00 | 3 / 3 |
| Self-MoA-Seq | 1.00 | 3 / 3 |

Self-MoA variants clearly outperform the mixed ensemble despite using the same proposer model.
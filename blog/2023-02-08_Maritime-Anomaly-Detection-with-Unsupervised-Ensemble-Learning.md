# Maritime Anomaly Detection with Unsupervised Ensemble Learning

08 Feb 2023

Anomaly detection is becoming increasingly significant in the maritime industry, where the detection of potential security threats and illegal activities such as piracy, smuggling, and human trafficking is critical. To ensure safe navigation and improve the efficiency of maritime operations, many companies are turning to machine learning techniques, such as anomaly detection, to detect unusual behavior in vessels. These anomalies could include deviations from planned routes, sudden changes in speed or heading, or collisions. This blog documents the details of the project I worked on as part of the Artificial Intelligence Labarotory course on Maritime Anomaly Detection at the University of Stuttgart, which aims to identify anomalies in maritime data and provide early warnings of potential security threats or illegal activities. We built an unsupervised ensemble system to detect anomalous vessel trajectories from AIS data. This blog focuses on the technical decisions: data pipeline design, algorithm selection, ensemble construction, and the evaluation challenges that come with having no ground truth labels.

## Problem Definition

The task is trajectory-level anomaly detection over maritime AIS data. An anomaly in this context is a vessel trajectory — or a segment of one — that deviates significantly from expected behavior in terms of speed, heading, or spatial position. Examples include:

- Sudden speed changes inconsistent with the vessel type or route
- Large, unexplained heading deviations
- Trajectories that enter unusual spatial regions (shallow water, restricted zones)

No labeled dataset exists for this problem in the general case, which rules out supervised approaches and makes evaluation non-trivial. The system must learn what "normal" looks like from data alone.

**Scope constraints:**
- Region: Long Beach, California (bounding box applied at preprocessing time)
- Vessel types: Cargo (including tankers) and Passenger
- Temporal resolution: 1-minute resampled time series

## Automatic Identification System (AIS) Data

AIS (Automatic Identification System) data is a mandatory broadcast signal from vessels, updated at intervals ranging from 2 seconds (for vessels under way) to 3 minutes (for vessels at anchor). The fields we worked with:

| Field | Description |
|---|---|
| MMSI | Maritime Mobile Service Identity — unique vessel ID |
| LAT, LON | Spatial position in decimal degrees |
| SOG | Speed Over Ground in knots |
| COG | Course Over Ground in degrees (0–360) |
| Heading | True heading of the vessel's bow in degrees |
| Vessel Type | Categorical: cargo, tanker, passenger, etc. |
| Draft, Length, Width | Physical vessel dimensions |

COG and Heading are related but distinct. COG is the actual direction of movement (affected by current and wind); Heading is where the bow points. The difference between them is the leeway angle, which itself can be a useful anomaly signal.

Raw AIS data is noisy: duplicate records, missing values, transmission gaps, and GPS errors are common. Before modelling, the data needs significant cleaning.

## Data Pipeline

### Preprocessing

The pipeline handled the following in order:

1. **Deduplication and NaN removal** — exact duplicate rows and rows with missing spatial or kinematic values were dropped.
2. **Stationary vessel filtering** — records with SOG = 0 were removed. Stationary vessels have a very different behavioral signature from vessels under way, and mixing them would confuse the models.
3. **Vessel type filtering** — only cargo and passenger vessel types were retained.
4. **Spatial filtering** — bounding box over the Long Beach region.
5. **Data type optimization** — downcasting numeric columns (e.g., `float64` → `float32`) to reduce memory pressure when working with large AIS archives.

### Trajectory Construction

From the filtered point data, per-vessel time series were constructed:

- **Temporal resampling at 1-minute intervals** — gaps were forward-filled up to a threshold; trajectories with large gaps were split.
- **Minimum trajectory length: 100 data points** (100 minutes of continuous signal). Shorter trajectories were discarded as too short to characterize behavior.
- **Feature engineering:**
  - Heading computed from consecutive lat/lon pairs using the haversine bearing formula
  - Speed derived from consecutive position deltas
  - Vectorized COG: COG decomposed into `sin(COG)` and `cos(COG)` to preserve angular continuity (avoiding the 0°/360° discontinuity)

The vectorization of COG is important. A raw COG value of 359° and one of 1° are 2° apart in reality but 358 apart numerically. Any distance-based model operating on raw COG will produce incorrect results near the wrap-around.

### Feature Set

The final feature vector per time step was:

    [LAT, LON, SOG, sin(COG), cos(COG), Heading]

## Ensemble Anomaly Detection

### Why an Ensemble?

A single unsupervised anomaly detector makes strong assumptions about the data distribution. Trajectories in a busy port region like Long Beach exhibit multi-modal behavior: vessels accelerating, decelerating, waiting at anchor, making port approaches. No single model captures all of this well. An ensemble pools the inductive biases of multiple algorithms, reducing the chance that a quirk in one model's assumptions produces systematic false positives or false negatives.

### Algorithms

**Gaussian Mixture Model (GMM)**

GMM models the data as a mixture of K Gaussian components. A point is anomalous if its likelihood under the fitted mixture is below a threshold:

    anomaly score = -log p(x) where p(x) = sum_k pi_k * N(x | mu_k, Sigma_k)

GMM is effective when the normal behavior clusters into distinct modes (e.g., vessels at different speeds in different corridor segments). The contamination fraction parameter controls what fraction of points are declared anomalous.

**K-Nearest Neighbors (KNN)**

The anomaly score of a point is the average distance to its K nearest neighbors. Points in sparse regions — far from any cluster of normal behavior — receive high scores. KNN makes no distributional assumption, which makes it robust to non-Gaussian data but sensitive to the choice of K and to high-dimensional spaces.

**Local Outlier Factor (LOF)**

LOF extends KNN by comparing the local density of a point to the local densities of its neighbors:

    LOF_k(x) = (1/k) * sum_{o in N_k(x)} lrd_k(o) / lrd_k(x)

where `lrd_k(x)` is the local reachability density of point x. A point with LOF >> 1 is in a sparser region than its neighbors, indicating an outlier. LOF handles heterogeneous density — a common property of port region AIS data where vessels cluster along shipping lanes but spread out in open water.

**One-Class SVM (OC-SVM)**

OC-SVM learns a decision boundary in a kernel-induced feature space that encloses the majority of training points. At inference time, points outside the boundary are anomalous. The key hyperparameters are the kernel (RBF in our case), `nu` (upper bound on the fraction of outliers), and `gamma` (RBF bandwidth). OC-SVM handles high-dimensional data well and makes no explicit distributional assumption, but it does not scale well to very large datasets.

**Isolation Forest (IF)**

Isolation Forest isolates anomalies rather than profiling normal behavior. It builds an ensemble of random decision trees, each constructed by repeatedly selecting a random feature and a random split value. Anomalous points — which occupy sparse, low-density regions — require fewer splits to isolate than normal points. The anomaly score is inversely proportional to the average path length across the tree ensemble:

    score(x) = 2^(-E[h(x)] / c(n))

where `h(x)` is the path length and `c(n)` is the expected path length for a dataset of size n. Isolation Forest is efficient (linear in n) and handles high-dimensional data without suffering from the curse of dimensionality as severely as distance-based methods.

**Clustering-Based Local Outlier Factor (CBLOF)**

CBLOF first clusters the data (using k-means), then computes an outlier score based on the size of the cluster a point belongs to and its distance to the nearest large cluster. Points in small clusters that are far from the main clusters receive high anomaly scores. This two-stage approach is more computationally tractable than computing full pairwise distances across the dataset.

### Voting Mechanism

Each model outputs a binary label per data point: normal (0) or anomalous (1). The **agreement score** for a point is the count of models that labelled it anomalous:

    agreement_score(x) = sum_{m in models} label_m(x)    where label_m(x) in {0, 1}

The agreement score ranges from 0 (no model flagged it) to 6 (all models agreed it is anomalous). This is a hard voting ensemble — each model has equal weight.

## Decision Function

The agreement score operates at the point level. We need a trajectory-level decision. The decision function has two thresholds:

1. **Point-level threshold (agreement score):** A point is considered anomalous if `agreement_score >= T_agreement`. We evaluated T_agreement ∈ {3, 4}.

2. **Trajectory-level threshold (anomaly fraction):** A trajectory is classified as anomalous if the fraction of anomalous points within it exceeds `T_fraction`. We evaluated T_fraction ∈ {0.05, 0.10}.

The full parameter space we evaluated:

| min_length | Duration (min) | outliers_fraction | T_agreement | T_fraction |
|---|---|---|---|---|
| 100 | 1 | 0.02 | 4 | 0.05 |
| 300 | 2 | 0.04 | 3 | 0.10 |

The two-level filter serves an important purpose: a single noisy GPS fix should not flag an entire voyage as anomalous. The trajectory-level threshold ensures that a meaningful proportion of the trajectory exhibits unusual behavior before it is labelled.

## Results

With `T_agreement = 4` and `T_fraction = 0.05`, the final classification was:

| | Normal points | Anomalous points | Normal trajectories | Anomalous trajectories |
|---|---|---|---|---|
| Count | 16,129 | 14 | 13,893 | 2,250 |

The small number of anomalous points relative to anomalous trajectories means most anomalous trajectories were flagged by a small but consistent cluster of unusual readings within an otherwise normal voyage — which is a realistic signature of, for example, a vessel briefly deviating from its lane.

### Cross-Type Generalization

The models were trained exclusively on cargo vessel trajectories. When tested on passenger vessels, the ensemble successfully flagged genuinely unusual passenger trajectories while leaving normal ones untouched. This suggests the learned notion of normality captures fundamental kinematic structure rather than vessel-type-specific patterns.

### Notable Finding: On-Land Trajectory

One flagged trajectory placed the vessel on land. This is a known AIS data artifact — GPS spoofing, signal multipath, or data entry error can produce impossible positions. The ensemble correctly identified this as anomalous despite no explicit spatial validity check in the feature set.

### False Positives and Explainability

Some flagged trajectories showed no obvious anomaly on visual inspection of their SOG, COG, and Heading time series. This is where the absence of ground truth labels makes evaluation hard. It is not possible to definitively classify these as false positives — they might reflect anomalies that are real but not visually obvious (e.g., spatial position relative to shipping lanes, which requires overlaying chart data). This points to the core explainability challenge in unsupervised anomaly detection: the model can output a score but cannot articulate which feature combination drove the decision.

## Challenges

**No ground truth labels.** All evaluation was qualitative (visual inspection of trajectories). Without labeled anomalies, quantitative metrics like precision, recall, and F1 cannot be computed. This makes it impossible to compare models rigorously or to tune thresholds in a principled way.

**Parameter sensitivity.** The contamination fraction `outliers_fraction` passed to each model has a large effect on how many points are flagged. Small changes to this parameter cascade into large changes in the agreement score distribution and ultimately in trajectory-level classifications. The two configurations we tested produced meaningfully different results.

**Computational cost.** Running six models over per-minute AIS time series for hundreds of vessels is expensive. OC-SVM in particular does not scale well; training time grows quadratically with the number of samples. In practice, subsampling or approximate methods would be needed for real-time operation.

**COG circularity.** Beyond vectorization, COG presents a challenge because vessels near ports frequently maneuver, producing rapidly changing COG values. This increases the variance of the COG features and can cause models to flag normal maneuvering as anomalous.

## Future Directions

**Labeled evaluation.** The most impactful improvement would be domain expert annotation of a subset of flagged trajectories. Even a few hundred labeled examples would allow proper precision-recall evaluation and threshold optimization.

**COLREGs-based rules.** The Convention on the International Regulations for Preventing Collisions at Sea defines legally required navigation behavior. Hard-coding these rules as a pre- or post-processing step would catch a class of anomalies that statistical models are not designed to detect.

**Deep sequence models.** LSTM autoencoders and Variational Autoencoders (VAEs) can learn compressed representations of normal trajectory sequences and flag trajectories that reconstruct poorly. Unlike the point-wise models used here, sequence models capture temporal dependencies across the full trajectory. The reconstruction error from an LSTM autoencoder provides a natural anomaly score without requiring a separate voting step.

**Additional data sources.** Ocean current and weather data, port entry/exit schedules, and vessel draft (to infer loading state) would all add context that pure AIS kinematics cannot provide.

**Real-time deployment.** A production system would require: streaming ingestion of AIS data, online or sliding-window model updates to handle concept drift (seasonal traffic changes, new shipping lanes), and a serving layer that can flag anomalies within seconds of the relevant data arriving.

---

The system works, produces interpretable outputs for obvious anomalies, and generalizes across vessel types — a strong result for a fully unsupervised approach on real-world data. The main open question is how well it handles the subtle cases that matter most operationally, which is ultimately an evaluation problem: with labeled ground truth, the remaining gaps become measurable and fixable. The future directions above are all tractable steps toward a production-grade system.

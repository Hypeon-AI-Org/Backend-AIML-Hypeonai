# Hypeon AI — Backend

The backend handles all data and API operations for Hypeon AI.

### Core Responsibilities

* Collect and process product data from **Amazon** and **Shopify**.
* Collect social discussions and engagement data from **Reddit** and **TikTok**.
* Clean, normalize, and unify all data into a single structure used by the platform.
* Provide internal APIs for:

  * Product insights (ratings, reviews, pricing)
  * Variant analysis (sizes, colors, price changes)
  * Category-level comparisons
  * Social trend insights from Reddit and TikTok discussions
* Manage database updates, caching, and background processing for large datasets.
* Serve data to the web app and AI models through internal endpoints.
* Handle authentication, request validation, and logging for all backend operations.

### In Short

It’s the system that connects raw e-commerce and social data → cleans and organizes it → makes it available to all Hypeon AI features through secure APIs.


---

# 🚀 Hypeon AI – Backend API Documentation

The **Hypeon AI Backend** powers the MVP analytics engine for multi-source product intelligence.
It integrates **Shopify, Amazon, TikTok, and Reddit** datasets to compute **growth, sentiment, engagement, trend, and hype metrics** for each niche or product.

---

## 🧠 Overview

### ✅ Core Capabilities

* Unified data from **Shopify**, **Amazon**, **TikTok**, and **Reddit**
* RESTful API built with **FastAPI**
* Real-time computation of:

  * **Growth Rate**
  * **Sentiment Score**
  * **Engagement Index**
  * **Trend Index**
  * **Hype Score (Composite Metric)**
* Supports both **niche-level** and **product-level** analytics
* Filterable by `niche`, `source`, and `level`

---

## ⚙️ Server Setup

### **1. Clone the Repository**

```bash
git clone https://github.com/<your-org>/hypeon-ai-backend.git
cd hypeon-ai-backend
```

### **2. Create a Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Start the Server**

```bash
uvicorn main:app --reload
```

> 🟢 Default server runs at: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**
> 🔍 Interactive API docs: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 🧩 API Endpoints

### **Root & Health**

| Method | Endpoint  | Description                                    | Example   |
| ------ | --------- | ---------------------------------------------- | --------- |
| `GET`  | `/`       | Returns basic API info and available endpoints | —         |
| `GET`  | `/health` | Checks data load and system status             | `/health` |

**Sample Response**

```json
{
  "status": "healthy",
  "dataframes_loaded": 5,
  "sources": ["shopify", "amazon", "tiktok", "reddit"]
}
```

---

### **1️⃣ Growth Metrics**

| Method | Endpoint          | Description                                |
| ------ | ----------------- | ------------------------------------------ |
| `GET`  | `/metrics/growth` | Returns niche or product-level growth rate |

**Parameters**

| Name     | Type   | Default   | Description                         |
| -------- | ------ | --------- | ----------------------------------- |
| `level`  | string | `"niche"` | `"niche"` or `"product"`            |
| `niche`  | string | —         | Optional niche filter               |
| `source` | string | `"all"`   | `"shopify"`, `"amazon"`, or `"all"` |

**Example**

```bash
GET /metrics/growth?level=product&niche=carpet&source=shopify
```

---

### **2️⃣ Sentiment Metrics**

| Method | Endpoint             | Description                                            |
| ------ | -------------------- | ------------------------------------------------------ |
| `GET`  | `/metrics/sentiment` | Returns aggregated sentiment data from Reddit & TikTok |

**Example Response**

```json
{
  "niche": "carpet",
  "sentiment_score": 0.74,
  "source_count": 2
}
```

---

### **3️⃣ Engagement Metrics**

| Method | Endpoint              | Description                                                  |
| ------ | --------------------- | ------------------------------------------------------------ |
| `GET`  | `/metrics/engagement` | Returns engagement index combining Reddit and TikTok metrics |

**Example**

```bash
GET /metrics/engagement?niche=carpet
```

**Example Response**

```json
{
  "niche": "carpet",
  "engagement_index": 0.52,
  "platforms": ["reddit", "tiktok"]
}
```

---

### **4️⃣ Trend Index**

| Method | Endpoint         | Description                                                       |
| ------ | ---------------- | ----------------------------------------------------------------- |
| `GET`  | `/metrics/trend` | Returns combined trend index using growth, sentiment & engagement |

**Example Response**

```json
{
  "trend_index": 0.68,
  "sources": ["shopify", "amazon", "reddit", "tiktok"]
}
```

---

### **5️⃣ Hype Score (Composite Metric)**

| Method | Endpoint        | Description                                                    |
| ------ | --------------- | -------------------------------------------------------------- |
| `GET`  | `/metrics/hype` | Returns final **Hype Score** (based on engagement + sentiment) |

**Formula**

```text
hype_score = 0.6 * engagement + 0.8 * sentiment
```

**Example**

```bash
GET /metrics/hype?niche=carpet
```

**Example Response**

```json
{
  "total_count": 10,
  "last_updated": "2025-11-03T13:05:45.426315Z",
  "data": [
    {"niche": "paint", "hype_score": 1.0},
    {"niche": "wallpaper", "hype_score": 0.96},
    {"niche": "furniture", "hype_score": 0.76},
    {"niche": "carpet", "hype_score": 0.62}
  ]
}
```

---

## 📊 Data Summary

| Source      | Records                            | Description                          |
| ----------- | ---------------------------------- | ------------------------------------ |
| **Amazon**  | 7,404 products / 78,092 variants   | Product & variant-level intelligence |
| **Shopify** | 12,585 products / 171,112 variants | E-commerce listings                  |
| **TikTok**  | 3,122 videos                       | Engagement & hashtag insights        |
| **Reddit**  | 856 posts / 11,291 comments        | Sentiment & discussion volume        |

---

## 🧠 Metric Sources & Logic

| Metric         | Sources         | Key Inputs                          |
| -------------- | --------------- | ----------------------------------- |
| **Growth**     | Shopify, Amazon | Reviews, rating change, price trend |
| **Sentiment**  | Reddit, TikTok  | Comments, captions, polarity        |
| **Engagement** | Reddit, TikTok  | Likes, upvotes, shares              |
| **Trend**      | Combined        | Weighted average of above metrics   |
| **Hype**       | All             | Engagement + Sentiment composite    |

---

## 🧪 Testing Summary

All endpoints tested successfully:

| Endpoint              | Status |
| --------------------- | ------ |
| `/`                   | ✅      |
| `/health`             | ✅      |
| `/metrics/growth`     | ✅      |
| `/metrics/sentiment`  | ✅      |
| `/metrics/engagement` | ✅      |
| `/metrics/hype`       | ✅      |
| `/metrics/trend`      | ✅      |

---

## 🖥️ Interactive Documentation

You can explore and test all endpoints using **Swagger UI**:

👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 🧾 License

This project is proprietary and developed as part of **Hypeon AI’s MVP platform**.
© 2025 Hypeon AI. All rights reserved.

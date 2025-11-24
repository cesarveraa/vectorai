
# 🧠 **Vector Attendance AI – Face API (Firebase + FastAPI)**

**Next-generation vector-based facial recognition for attendance systems.**

🔗 **Live Dashboard:** [https://attendance-ai-kappa.vercel.app/](https://attendance-ai-kappa.vercel.app/)  
📁 **API Backend Repo:** [https://github.com/cesarveraa/attendance-ai](https://github.com/cesarveraa/attendance-ai)  
📁 **Video/Frontend Demo Repo:** [https://github.com/cesarveraa/vector_video](https://github.com/cesarveraa/vector_video)

---

## ⚠️ **Legal & Ethical Notice**

This project handles **biometric facial data**. Before using in production:

- ✔️ Obtain **explicit user consent**
- ✔️ Provide a **privacy policy** and explain how biometrics are stored
- ✔️ Implement secure data retention/deletion processes
- ✔️ Comply with local data protection laws

---

# 🚀 **About the API**

Vector Attendance AI is a fully modular attendance system powered by:

- 🔥 **FastAPI backend**
- 🔐 **Firebase integration (Auth + DB)**
- 🧬 **Face vector embeddings (128–512d)**
- 🎥 **Image processing endpoints**
- 📊 **Modern React Dashboard**
- 🤖  Automation via **IBM watsonx Orchestrate** try it in the page: [https://attendance-ai-kappa.vercel.app/](https://attendance-ai-kappa.vercel.app/)  on the chat    
you can try: "gimme the report of the persons who arrived late"
<img width="346" height="501" alt="image" src="https://github.com/user-attachments/assets/10549041-877c-4b06-b004-25475151b58d" />


All API routes use the prefix:

```http
/api/v1
````

Authentication is required via header:

```http
X-API-Key: <INTERNAL_SECRET>
```

-----

# 📁 **Endpoints**

-----

## 🔐 **Authentication**

Every request must include the API Key in the headers:

```http
X-API-Key: <INTERNAL_SECRET>
```

-----

## 👥 **Clients (CRUD)**

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/clients` | Create a client `{id, name?, meta?}` |
| **GET** | `/clients?limit=100` | List clients |
| **GET** | `/clients/{id}` | Fetch a single client |
| **PATCH** | `/clients/{id}` | Update `{name?, meta?}` |
| **DELETE** | `/clients/{id}` | Remove client |

-----

## 🧬 **Vector Registration**

### ➤ **Register a vector embedding**

Directly register a pre-calculated vector.

```http
POST /clients/{id}/face-vectors
Content-Type: application/json

{
  "vector": [0.12, 0.33, 0.91, ...]
}
```

### ➤ **Register face from an image**

Upload an image to automatically extract and store the face vector.

**POST** `/clients/{id}/face-image`

  * **Accepts:** `multipart/form-data`
  * **Process:**
    1.  Extracts face from image
    2.  Generates embedding
    3.  Stores it under the client automatically

-----

## 🎯 **Face Detection (Two Modes)**

### 1️⃣ Detect via vector

Send a raw vector to find a match in the database.

```http
POST /detect/vector
Content-Type: application/json

{
  "vector": [...],
  "threshold": 0.6
}
```

### 2️⃣ Detect via image

Upload an image file to detect a face and find a match.

```http
POST /detect/image?threshold=0.6
Content-Type: multipart/form-data
```

### 📤 Sample Response

```json
{
  "matched": true,
  "client_id": "abc12345",
  "score": 0.78,
  "message": "Face recognized"
}
```

-----

# 📊 **Dashboard Overview**

The system includes a full-featured modern dashboard:

  * 🧑‍💼 **Client management**
  * 🧪 **Real-time detection tester**
  * 🎥 **Camera feed demo** (video preview)
  * 📘 **Daily attendance reports**
  * 📈 **Analytics** for punctuality & patterns
  * ✨ **Clean UI** built with Tailwind + ShadCN

🔗 **Live demo:** [https://attendance-ai-kappa.vercel.app/](https://attendance-ai-kappa.vercel.app/)

-----

# 🛠️ **Repositories**

  * 🔵 **Backend (FastAPI + Firebase):** [https://github.com/cesarveraa/attendance-ai](https://github.com/cesarveraa/attendance-ai)

  * 🎥 **Frontend + Video Demo:** [https://github.com/cesarveraa/vector\_video](https://github.com/cesarveraa/vector_video)

-----

# 🧩 **Tech Stack**

| Component | Technology |
| :--- | :--- |
| **Backend** | FastAPI, Python |
| **Database** | Firebase |
| **Vector System** | Face embeddings (128–512d) |
| **Frontend** | React, Vite, Tailwind, ShadCN |
| **Hosting** | Vercel (Frontend), Render/Railway (API) |
| **Automation** | IBM watsonx Orchestrate (Optional) |

-----

# 📜 **License**

**MIT License.** Use freely for research, learning, or commercial development (with proper compliance for biometric processing).

-----

# 🙌 **Contributing**

Pull requests are welcome. For major changes, open an issue first to discuss your idea.

-----

# ⭐ **Support**

If you like this project, please ⭐ the repo:  
[https://github.com/cesarveraa/attendance-ai](https://github.com/cesarveraa/attendance-ai)

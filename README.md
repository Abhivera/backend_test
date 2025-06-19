---

```markdown
# Full-stack Keypoint & Image Capture System

This project provides a backend system for extracting human pose keypoints from images using MediaPipe (Python), storing keypoints in PostgreSQL (Neon), images in MongoDB Atlas, and providing a REST API with daily backup and email notification.

---

## Features

- Extracts 33 body keypoints from images using MediaPipe (Python)
- Stores keypoints in PostgreSQL (Neon)
- Stores original images in MongoDB Atlas
- REST API for full CRUD operations
- Daily cron job to backup both databases and email the ZIP file

---

## Tech Stack

- **Backend:** Node.js (Express)
- **Image Processing:** Python + MediaPipe
- **SQL DB:** PostgreSQL (Neon)
- **NoSQL DB:** MongoDB Atlas
- **Cron Jobs:** node-cron
- **Zipping:** archiver (Node.js)
- **Email:** Nodemailer/SendGrid

---

## Getting Started

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd python_image
```

---

### 2. Python API Setup

#### a. Install Python dependencies

```bash
pip install -r requirements.txt
```

#### b. Start the Python API server

```bash
python pose_extractor.py --mode api --host 127.0.0.1 --port 5001
```

- The API will be available at `http://127.0.0.1:5001`

---

### 3. Node.js Backend Setup

#### a. Go to the backend folder

```bash
cd node_backend
```

#### b. Install Node.js dependencies

```bash
npm install
```

#### c. Create a `.env` file

Create a file named `.env` in `node_backend/` with the following content (replace with your actual credentials):

```
PORT=5000

# Python API URL
PYTHON_API_URL=http://127.0.0.1:5001/extract-pose

# Neon PostgreSQL
PG_URI=postgresql://test_owner:npg_gSaRTy45IHXJ@ep-super-bread-a11pxc7v-pooler.ap-southeast-1.aws.neon.tech/test?sslmode=require

# MongoDB Atlas
MONGO_URI=mongodb+srv://abhi123:abhi123@cluster0.8zjytoa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

# Email (update with your real credentials)
EMAIL_USER=your@email.com
EMAIL_PASS=yourpassword
EMAIL_TO=recipient@email.com
```

#### d. Start the Node.js backend

```bash
node src/app.js
```

- The backend will run at `http://localhost:5000`

---

### 4. Database Setup

#### a. PostgreSQL (Neon)

- Create the `keypoints` table in your Neon PostgreSQL database:

```sql
CREATE TABLE keypoints (
    id SERIAL PRIMARY KEY,
    image_id VARCHAR(255) NOT NULL,
    keypoints JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### b. MongoDB Atlas

- No manual setup needed; images will be stored automatically.
- Make sure your IP is whitelisted in MongoDB Atlas.

---

### 5. API Usage

#### a. Extract pose from an image

```bash
curl -X POST -F "image=@/path/to/your/image.jpg" http://localhost:5000/api/extract-pose
```

#### b. Fetch keypoints

```bash
curl http://localhost:5000/api/keypoints/<image_id>
```

#### c. Fetch image

```bash
curl http://localhost:5000/api/images/<image_id> --output output.jpg
```

#### d. Update keypoints

```bash
curl -X PUT -H "Content-Type: application/json" -d '{"keypoints": {...}}' http://localhost:5000/api/keypoints/<image_id>
```

#### e. Delete keypoints and image

```bash
curl -X DELETE http://localhost:5000/api/keypoints/<image_id>
```

---

### 6. Cron Job and Backups

- The cron job runs daily at 11:59 PM, creates a ZIP backup of both databases, and emails it to the configured address.
- Backups are stored in `node_backend/backup/`.

---

### 7. Troubleshooting

- Ensure both Python and Node.js servers are running.
- Check your `.env` for correct database and email credentials.
- For database connection issues, verify your Neon and MongoDB Atlas settings.

---

### 8. Screenshots & Sample Data

- Use Postman or curl to test endpoints.
- Backups and sample data will appear in `node_backend/backup/`.

---

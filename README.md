# 🏔️ Mountain Coder

**The Offline-First, Dockerized Coding Interview Platform.**

Mountain Coder is a self-hosted, full-stack application designed for practicing data structures and algorithms (DSA) **locally**. It replicates the interview experience and online flows of judges like LeetCode and HackerRank, but with a focus on privacy, offline capability, and raw performance.

It features a **"Serverless-State" architecture**, meaning your progress, code history, and notes are stored entirely in your browser (LocalStorage), keeping the backend stateless and blazing fast. **Everything runs 100% on your machine within Docker.**

---

## 📸 Screenshots

| **Dashboard & Study Plans** | **IDE & Engineering Notebook** |
|:---------------------------:|:------------------------------:|
| ![Dashboard](screenshots/dashboard.png) | ![Editor](screenshots/editor.png) |
| *Filter by topic, difficulty, or search.* | *Monaco Editor with real-time feedback.* |
| ![Dashboard](screenshots/question_bank.png) |
| *QuestionBank* |

---

## 🚀 Key Features

* **🔒 Secure Sandbox:** Runs user code (Python & Java) inside isolated Docker containers using a robust Judge system.
* **⚡ Offline-First Design:** All assets (including the Monaco Editor) are bundled locally. Practice without internet.
* **🧠 Engineering Notebook:** Built-in tab to write pseudocode, complexity analysis, or notes alongside your solution (Auto-saved).
* **💾 Smart State:**
    * **Auto-Save:** Code is saved to your browser instantly as you type.
    * **Progress Tracking:** Tracks "Solved" ✅ and "Attempted" ⚠️ status without a database user session.
* **🛠️ Developer Experience:** One command setup. Automated data ingestion pipeline loads questions on startup.

---

### ✨ Features Overview

#### 1. 📊 Interactive Dashboard & Discovery

* **Curated Study Plans:** Browse "Cards" (e.g., "Top 100 Questions") that group essential problems together.
* **Smart Filtering:** Instantly filter questions by **Topic** (Arrays, Trees, DP, etc.) or **Difficulty** (Easy, Medium, Hard).
* **Global Search:** Real-time search bar to find problems by title or keywords.
* **Visual Progress Indicators:** See at a glance which study plans you are actively working on.

#### 2. 💻 Full-Featured Coding Workspace (IDE)

* **Professional Editor:** Integrated **Monaco Editor** (the engine powering VS Code) with syntax highlighting, auto-indentation, and line numbers.
* **Multi-Language Support:** First-class support for **Python 3** and **Java 17**.
* **Tabbed Interface:**
* **📖 Description:** Clean Markdown rendering with **MathJax** support for complex mathematical formulas.
* **💡 Hints:** Stuck? Reveal progressive hints without spoiling the solution.
* **📝 Engineering Notebook:** A dedicated scratchpad for pseudocode, complexity analysis, or thoughts. **Auto-saved locally.**
* **🔓 Solution:** Access the official solution approach when needed.


* **Customizable Layout:** Resizable panes and distraction-free dark mode interface.

#### 3. ⚡ "Serverless-State" & Local Persistence

* **Auto-Save Everywhere:** Never lose your work. Your code and notes are automatically saved to your browser's Local Storage as you type.
* **Offline Progress Tracking:** The app tracks your "Solved" ✅ and "Attempted" ⚠️ status locally—no account creation or server login required.
* **Code History:** Remembers your last solution for every problem, allowing you to pick up exactly where you left off.

#### 4. 🚀 Execution & Judging Engine

* **One-Click Run & Submit:**
* **Run Code (`Ctrl + Enter`):** Test your logic against a sample case or **Custom Input**.
* **Submit (`Ctrl + Shift + Enter`):** Validate your solution against a suite of hidden test cases.


* **Detailed Feedback:** Receive instant feedback on **Status** (Accepted/Wrong Answer), **Runtime** (in ms), and specific **Test Case Failures** (Expected vs. Actual output).
* **Secure Sandbox:** All code executes inside isolated Docker containers, ensuring safety and consistency.
* **Reset Functionality:** One-click "Reset to Boilerplate" to start fresh on any problem.

#### 5. 🛠️ Developer Experience

* **Keyboard Shortcuts:** Pro-style shortcuts for running and submitting code without leaving the keyboard.
* **Zero-Config Setup:** Fully Dockerized. Run `docker-compose up` and the database seeds itself automatically.
* **Hot-Reload Frontend:** Lightweight vanilla JavaScript architecture means the UI is snappy and responsive.


## 🛠️ Tech Stack

* **Frontend:** Vanilla JavaScript (ES6+), CSS3 Variables (Dark Mode), Monaco Editor.
* **Backend:** Python 3.12, FastAPI, Uvicorn.
* **Execution Environment:** Docker (Alpine/Slim containers).
* **Database:** SQLite / SQLAlchemy.

---

## 🏁 Getting Started

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/pragmaticdesign-dev/mountain-coder.git](https://github.com/pragmaticdesign-dev/mountain-coder.git)
    cd mountain-coder
    ```

2.  **Build and Run**
    Run the application using Docker Compose. This automates everything (Server start + Data Import).
    ```bash
    docker-compose up --build
    ```

3.  **Access the App**
    Open your browser and navigate to:
    ```
    http://localhost:8000
    ```

### 🎮 How to Use
Since Mountain Coder runs entirely locally, the workflow is simple:
1.  **Browse Questions:** Use the Dashboard to filter by topic (e.g., Arrays, Trees) or difficulty.
2.  **Code:** Select a problem. The editor supports Python and Java.
3.  **Run & Submit:** * **Run:** Executes your code against a sample test case inside a secure Docker container.
    * **Submit:** Runs your code against all hidden test cases.
4.  **Save Notes:** Use the "Notebook" tab to jot down complexity analysis. This is saved to your browser automatically.

---

## 🔄 Updates & Maintenance

### Getting New Questions (Git Pull)
If you pull the latest changes from GitHub (`git pull`) and notice that new questions are not appearing, you must perform a manual reset of the database.

**Steps to apply updates:**
1.  Stop the container.
2.  **Delete the `app/data` folder.**
3.  Rebuild and run: `docker-compose up --build`

*Note: We are working on an automated migration system. Until then, deleting `app/data` is the required workaround to force the application to re-seed the database with the latest questions.*

---

## 🔧 Troubleshooting

### 1. Database or Question Issues (Reset Backend)
If questions are missing or the database behaves unexpectedly, follow the "Updates & Maintenance" steps above to delete `app/data` and rebuild.
```bash
# Linux/Mac
rm -rf app/data

# Windows (PowerShell)
Remove-Item -Recurse -Force app/data

```

### 2. Progress or UI Issues (Reset Frontend)

If your "Solved" status isn't updating or the editor behaves strangely, you can clear your browser's local storage.

⚠️ **CAUTION:** Deleting Local Storage will **permanently erase** your "Solved" status, saved code snippets, and engineering notes. Since this app is "Serverless-State," your browser is the only place this data exists. Only proceed if you are willing to lose your progress.

1. Open your browser's Developer Tools (`F12` or `Right Click -> Inspect`).
2. Go to the **Application** tab -> **Local Storage**.
3. Right-click `http://localhost:8000` and select **Clear**.
4. Refresh the page.


### 3. Slow Java Compilation (Performance Tuning)

If you are a Java developer and notice slow compilation times, the default CPU limits in Docker might be too restrictive.

1. Open `docker-compose.yml`.
2. Locate the `cpus: '0.85'` setting.
3. Increase it to **1 core or more** (e.g., `'1.5'` or `'2.0'`) to speed up the process.

```yaml
    deploy:
      resources:
        limits:
          cpus: '1.5'    # Increase to 1.5 cores or more

```


## 📂 Project Structure

```text
mountain-coder/
├── app/
│   ├── data/           # SQLite database persistence (Auto-generated)
│   ├── routers/        # API Endpoints (Judge, Questions)
│   ├── utils/          # Docker Sandbox Logic
│   ├── static/         # Frontend Assets (JS, CSS, Monaco)
│   └── templates/      # HTML Files
├── import_data/        # JSON Question Data (Auto-imported)
├── import_script.py    # Script to load data into DB
├── Dockerfile          # Container definition
├── docker-compose.yml  # Orchestration
└── requirements.txt    # Python dependencies

```